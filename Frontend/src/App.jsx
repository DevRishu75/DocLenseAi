// React hooks let a function component remember values, react to changes, and
// hold references to DOM elements. The icons below are presentational only.
import { useEffect, useRef, useState } from 'react'
import {
  ArrowDownToLine, ArrowRight, ArrowUp, Check, ChevronDown, Menu, Trash2, Pencil,
  FileText, Files, FolderOpen, HelpCircle, LoaderCircle, LogOut, MessageSquareText,
  MoreHorizontal, Plus, Search, ShieldCheck, Sparkles, Upload, X,
} from 'lucide-react'

// Vite exposes client-side environment variables through import.meta.env.
// This fallback is useful when running the frontend locally.
// const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Keep auth header formatting in one place so every protected request is
// consistent. A bearer token proves the signed-in user's identity to the API.
// const authHeaders = (token) => ({ Authorization: `Bearer ${token}` })
const authHeaders = (token) =>({Authorization: `Bearer ${token}`})

// Shared API helper: fetch the endpoint, parse JSON, and turn API failures into
// Error objects so callers can show a useful message in the UI.
// async function request(path, options = {}, token) {
//   const response = await fetch(`${API}${path}`, {
//     ...options,
//     headers: {
//       ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
//       ...(token ? authHeaders(token) : {}),
//       ...options.headers,
//     },
//   })
//   const data = await response.json().catch(() => ({}))
//   if (!response.ok) {
//     const detail = data.detail
//     throw new Error(typeof detail === 'string' ? detail : detail?.message || data.message || 'Something went wrong. Please try again.')
//   }
//   return data
// }
async function request(path,options={},token){
  const {headers: customHeaders,...fetchOptions} = options
  const headers = new Headers(customHeaders)
   // Add a default content type only when a body exists.
  // FormData needs the browser to generate its own boundary.
  if (fetchOptions.body != null && !(fetchOptions.body instanceof FormData) && !headers.has('Content-Type')){
    headers.set('Content-Type','application/json')
  }
  // The supplied token takes precedence over custom headers.
  if(token){
    const auth = authHeaders(token)
    headers.set('Authorization',auth.Authorization)
  }
  const response = await fetch(`${API}${path}`,{
    ...fetchOptions,
    headers,
  })
  if (response.status === 401) {
    localStorage.removeItem('docLenseAI_access_token')
    localStorage.removeItem('docLenseAI_email')
    window.dispatchEvent(new Event('docLenseAI:session-expired'))
  }
  // Handle responses that have no body.
  let data
  if(response.status === 204){
    data = {}
  }
  else {
    const contentType = response.headers.get('Content-Type')||''
    if(contentType.includes('application/json')){
      data = await response.json().catch(()=> null)
    }
    else{
      data = await response.text().catch(()=> '')
    }
  }
  if (!response.ok) {
    const detail =
      data && typeof data === 'object' ? data.detail : null

    const message =
      typeof detail === 'string'
        ? detail
        : typeof detail?.message === 'string'
          ? detail.message
          : typeof data?.message === 'string'
            ? data.message
            : `Request failed (${response.status})`

    throw new Error(message)
  }
return data

}


function App() {
  // useState stores UI data. Calling its setter schedules a render with the
  // updated value. The lazy initializer reads saved credentials only once.
  const [token, setToken] = useState(() => localStorage.getItem('docLenseAI_access_token') || '')
  const [email, setEmail] = useState(() => localStorage.getItem('docLenseAI_email') || '')
  const [documents, setDocuments] = useState([])
  const [activeId, setActiveId] = useState('')
  const [history, setHistory] = useState([])
  const [question, setQuestion] = useState('')
  const [loadingDocs, setLoadingDocs] = useState(false)
  const [sending, setSending] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [authMode, setAuthMode] = useState('login')
  const [authEmail, setAuthEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [search, setSearch] = useState('')
  const [showSources, setShowSources] = useState(true)
  const [page, setPage] = useState('home')
  const [menuOpen, setMenuOpen] = useState(false)
  const [documentMenu, setDocumentMenu] = useState('')
  const [nicknames, setNicknames] = useState(() => JSON.parse(localStorage.getItem('docLenseAI_nicknames') || '{}'))
  // useRef holds DOM nodes without triggering a render. These refs let buttons
  // open the hidden file picker and let us focus the question box after sending.
  const fileRef = useRef(null)
  const promptRef = useRef(null)
  const activeDoc = documents.find((doc) => doc.document_id === activeId)

  // Effects synchronize React with things outside rendering: load the user's
  // documents when their token changes, and scroll the chat as it grows.
  useEffect(() => {
    if (token) loadDocuments()
  }, [token])

  useEffect(() => {
    const handleExpiredSession = () => signOut()
    window.addEventListener('docLenseAI:session-expired', handleExpiredSession)
    return () => window.removeEventListener('docLenseAI:session-expired', handleExpiredSession)
  }, [])

  useEffect(() => {
    if (!token) return
    let timeoutId
    try {
      const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')))
      if (payload.exp) {
        const remaining = payload.exp * 1000 - Date.now()
        if (remaining <= 0) signOut()
        else timeoutId = window.setTimeout(signOut, remaining)
      }
    } catch {
      // The API response handler signs out if the server rejects an invalid token.
    }
    return () => window.clearTimeout(timeoutId)
  }, [token])

  useEffect(() => {
    const pane = document.querySelector('.conversation-scroll')
    if (pane) pane.scrollTop = pane.scrollHeight
  }, [history, sending])

  async function loadDocuments(preferredId) {
    // Async event helpers can await network requests; loading state drives the
    // spinner while the request is in progress. finally runs on success/failure.
    setLoadingDocs(true)
    try{
      const docs = await request('/api/v1/documents',{},token)
      setDocuments(docs)
      setActiveId((current)=> preferredId || (docs.some((doc)=>doc.document_id===current)?current:docs[0]?.document_id||''))
    }
    catch(err){
      
      if(/token|unauthorized|credentials/i.test(err.message)){
        signOut()
      }
      else{
        setError(err.message)
      }
      
    }
    finally{
        setLoadingDocs(false)
        if(fileRef.current) fileRef.current.value = ''
      }
  }

  async function submitAuth(event) {
    // Prevent the browser's default full-page form submission. Registration is
    // followed by login so this flow ends with a token either way.
    event.preventDefault(); setError('')
    try {
      if (authMode === 'register') {
        await request('/api/v1/auth/register', { method: 'POST', body: JSON.stringify({ email: authEmail, password }) })
      }
      const result = await request('/api/v1/auth/login', { method: 'POST', body: JSON.stringify({ email: authEmail, password }) })
      // localStorage.setItem('docLenseAI_access_token', result.access_token)
      // localStorage.setItem('docLenseAI_email', authEmail)
      // setEmail(authEmail); setToken(result.access_token)
      localStorage.setItem('docLenseAI_access_token',result.access_token)
      localStorage.setItem('docLenseAI_email',authEmail)
      setEmail(authEmail); setToken(result.access_token)
    } catch (err) { setError(err.message) }
  }

  function signOut() {
    // Clear persisted credentials as well as React state so private data is no
    // longer shown after sign-out.
    // localStorage.removeItem('docLenseAI_access_token'); localStorage.removeItem('docLenseAI_email')
    // setToken(''); setDocuments([]); setActiveId(''); setHistory([]); setEmail('')
    localStorage.removeItem('docLenseAI_access_token')
    localStorage.removeItem('docLenseAI_email')
    setToken(''); setDocuments([]); setActiveId(''); setHistory([]); setEmail('')
    setPage('home'); setMenuOpen(false)
    setAuthEmail(''); setPassword(''); setError(''); setAuthMode('login')
  }

  async function deleteDocument(doc) {
    if (!window.confirm(`Delete “${doc.filename}”?`)) return
    try {
      await request(`/api/v1/documents/${doc.document_id}`, { method: 'DELETE' }, token)
      const remaining = documents.filter((item) => item.document_id !== doc.document_id)
      setDocuments(remaining)
      setNicknames((current) => {
        const next = { ...current }; delete next[doc.document_id]
        localStorage.setItem('docLenseAI_nicknames', JSON.stringify(next)); return next
      })
      if (activeId === doc.document_id) { setActiveId(remaining[0]?.document_id || ''); setHistory([]) }
      setDocumentMenu('')
    } catch (err) { setError(err.message) }
  }

  function renameDocument(doc) {
    const nickname = window.prompt('Document nickname', nicknames[doc.document_id] || doc.filename)
    if (nickname === null) return
    const next = { ...nicknames }
    if (nickname.trim() && nickname.trim() !== doc.filename) next[doc.document_id] = nickname.trim()
    else delete next[doc.document_id]
    setNicknames(next); localStorage.setItem('docLenseAI_nicknames', JSON.stringify(next)); setDocumentMenu('')
  }


  async function uploadFiles(files) {
    // The file input and drag/drop both provide a FileList; this app accepts one
    // // PDF at a time. FormData is used for file uploads (not JSON).
    // const file = files?.[0]
    // if (!file) return
    // setError(''); setNotice('');
    // if (!file.name.toLowerCase().endsWith('.pdf')) { setError('Please choose a PDF file.'); return }
    // setUploading(true)
    // const body = new FormData(); body.append('file', file)
    // try {
    //   const result = await request('/api/v1/uploads', { method: 'POST', body }, token)
    //   setNotice(`${file.name} is ready to explore.`)
    //   await loadDocuments(result.document_id)
    //   setHistory([])
    // } catch (err) { setError(err.message) }
    // finally { setUploading(false); if (fileRef.current) fileRef.current.value = '' }
    const file = files?.[0]
    if(!file)return
    setError(''); setNotice('')
    if(!file.name.toLowerCase().endsWith('.pdf')){
      setError('Please choose a PDF file.')
      return
    }
    setUploading(true)
    const body = new FormData()
    body.append('file',file)
    try{
      const result = await request('/api/v1/uploads',{method:'POST',body},token)
      setNotice(`${file.name}is ready to explore.`)
      await loadDocuments(result.document_id)
      setHistory([])
    }
    catch(err){
      setError(err.message)
    }
    finally{
      setUploading(false)
      if(fileRef.current) fileRef.current.value = ''
    }
  }

  async function ask(value = question) {
    // Add the question immediately for responsive UI, then replace that last
    // entry with the API answer (or an error) when the request finishes.
   const text = value.trim()
   if(!text || !activeId || sending) return
   setError('')
   setQuestion('')
   setNotice('')
   setHistory((items)=>[...items, {question:text,answer:null}])
   setSending(true)
   try{
    const result = await request(`/api/v1/ask/${activeId}`,{method:'POST',body:JSON.stringify({question:text})},token)
   setHistory((items)=>items.map((item,index)=>index===items.length-1?{...item,answer:result.answer,sources:result.sources || []}:item))
   }
   catch(err){
    setHistory((items)=>items.map((item,index)=>index===items.length-1?{...item,answer:`I could not find the information regarding your question. Please try rephrasing it or ask a different question. ${err.message}`,failed:true,sources:[]}:item))
   }
   finally{
    setSending(false)
    promptRef.current?.focus()
   }

  }

  // This is conditional rendering: unauthenticated users see the auth
  // component; authenticated users continue to the document workspace below.
  if (!token) return <AuthScreen {...{ authMode, setAuthMode, authEmail, setAuthEmail, password, setPassword, submitAuth, error, setError }} />

  const filteredDocs = documents.filter((doc) => `${doc.filename} ${nicknames[doc.document_id] || ''}`.toLowerCase().includes(search.toLowerCase()))
  // JSX describes the UI as a tree. Curly braces embed JavaScript expressions,
  // and handlers such as onClick update state or start async work.
  return (
    <div className="app-shell">
      <aside className={`sidebar ${menuOpen ? 'menu-open' : ''}`}>
        <a className="brand" href="#home" aria-label="docLenseAI home"><span className="brand-mark"><Files size={18} strokeWidth={2.2} /></span><span>docLenseAI</span></a>
        <div className="quick-nav"><button onClick={() => { setPage('home'); setMenuOpen(false) }}><MessageSquareText size={16} /> Chat with DocLense AI</button><button onClick={() => { setPage('documents'); setMenuOpen(false) }}><FolderOpen size={16} /> Documents list</button><button onClick={signOut}><LogOut size={16} /> Log out</button></div>
        <div className="workspace-label">WORKSPACE</div>
        <div className="sidebar-nav"><button className={`nav-item ${page === 'documents' ? 'selected' : ''}`} onClick={() => { setPage('documents'); setMenuOpen(false) }}><FolderOpen size={17} /> My documents <span className="nav-count">{documents.length}</span></button></div>
        <div className="sidebar-section"><div className="section-title">YOUR LIBRARY <button className="icon-button tiny" onClick={() => fileRef.current?.click()} aria-label="Upload a document"><Plus size={16} /></button></div>
          <label className="search-box"><Search size={15} /><input placeholder="Find a document" value={search} onChange={(e) => setSearch(e.target.value)} /><kbd>⌘ K</kbd></label>
          <div className="document-list">
            {loadingDocs ? <div className="sidebar-empty"><LoaderCircle className="spin" size={17} /> Loading documents…</div> : filteredDocs.length ? filteredDocs.map((doc) => (
              <div key={doc.document_id} className={`document-row ${activeId === doc.document_id ? 'active' : ''}`}><button className="document-item" onClick={() => { setPage('documents'); setActiveId(doc.document_id); setHistory([]); setError(''); setNotice(''); setMenuOpen(false) }}>
                <span className="pdf-icon"><FileText size={16} /></span><span className="document-name">{nicknames[doc.document_id] || doc.filename}</span>
              </button><button className="icon-button tiny doc-menu-button" aria-label={`Options for ${doc.filename}`} onClick={() => setDocumentMenu(documentMenu === doc.document_id ? '' : doc.document_id)}><MoreHorizontal size={15} /></button>{documentMenu === doc.document_id && <div className="document-menu"><button onClick={() => renameDocument(doc)}><Pencil size={14} /> Add nickname</button><button className="delete-action" onClick={() => deleteDocument(doc)}><Trash2 size={14} /> Delete</button></div>}</div>
            )) : <div className="sidebar-empty">{search ? 'No matching documents.' : 'Your documents will appear here.'}</div>}
          </div>
        </div>
        <div className="sidebar-bottom"><button className="side-link"><HelpCircle size={16} /> Help center <ArrowRight size={14} /></button><div className="profile"><div className="avatar">{email.slice(0, 1).toUpperCase()}</div><div className="profile-copy"><strong>{email.split('@')[0]}</strong><span>{email}</span></div><button className="icon-button" onClick={signOut} title="Sign out" aria-label="Sign out"><LogOut size={16} /></button></div></div>
      </aside>

      <main className="main-panel">
        <header className="topbar"><button className="icon-button menu-toggle" aria-label="Open navigation" onClick={() => setMenuOpen(!menuOpen)}><Menu size={19} /></button><div className="breadcrumbs"><span>Workspace</span><span className="crumb-slash">/</span><strong>{page === 'home' ? 'Home' : (activeDoc ? nicknames[activeId] || activeDoc.filename : 'My documents')}</strong></div><div className="topbar-actions"><span className="secure-label"><ShieldCheck size={15} /> Private workspace</span><button className="avatar avatar-small" title={email} aria-label="Go to home" onClick={() => { setPage('home'); setMenuOpen(false) }}>{email.slice(0, 1).toUpperCase()}</button></div></header>
        <div className="work-area">
          {page === 'home' ? <section className="home-screen"><div className="home-brand" aria-label="DOCLENSEAI"><span>DOCLENSEAI</span></div><button className="home-chat-button" onClick={() => { setPage('documents'); if (activeDoc) setHistory([]) }}><MessageSquareText size={18} /> Chat with DocLense AI <ArrowRight size={16} /></button><button className="home-documents-link" onClick={() => setPage('documents')}>Open documents <span>{documents.length}</span></button></section> : <>
          {!activeDoc ? <EmptyState uploading={uploading} onUpload={() => fileRef.current?.click()} onDrop={uploadFiles} /> : <>
            <div className="document-heading"><div className="file-cover"><FileText size={24} /></div><div className="heading-copy"><div className="eyebrow">DOCUMENT WORKSPACE</div><h1>{activeDoc.filename}</h1><p>Added {new Date(activeDoc.created_at).toLocaleDateString(undefined, { month: 'long', day: 'numeric', year: 'numeric' })} <span>·</span> PDF document</p></div><button className="button button-secondary heading-action" onClick={() => fileRef.current?.click()}><Plus size={16} /> Add document</button></div>
            <div className="chat-card">
              <div className="chat-topline"><div className="chat-title"><span className="sparkle-icon"><Sparkles size={16} /></span><div><strong>Ask your document</strong><small>Answers grounded in your file</small></div></div><button className="icon-button" title="New conversation" onClick={() => { setHistory([]); setError(''); setNotice('') }}><MessageSquareText size={17} /></button></div>
              <div className={`conversation-scroll ${history.length ? 'has-history' : ''}`}>
                {!history.length ? <div className="welcome-state"><div className="welcome-art"><span className="art-sheet sheet-back"></span><span className="art-sheet sheet-front"><i></i><i></i><i></i><b><Sparkles size={17} /></b></span><span className="art-spark spark-one">✳</span><span className="art-spark spark-two">✦</span></div><h2>A little less searching.<br /><span>A lot more understanding.</span></h2><p>Ask a question about this document and get a clear answer with references to the source.</p><div className="suggestion-row"><button onClick={() => ask('Summarize the key points in this document')}>Summarize the key points <ArrowRight size={14} /></button><button onClick={() => ask('What are the main dates and deadlines?')}>Find dates & deadlines <ArrowRight size={14} /></button></div></div> : <div className="conversation-content">{history.map((item, index) => <div className="turn" key={`${item.question}-${index}`}><div className="user-question"><div className="avatar avatar-mini">{email.slice(0, 1).toUpperCase()}</div><p>{item.question}</p></div><div className="assistant-answer"><div className="answer-avatar"><Sparkles size={15} /></div><div className="answer-body">{item.answer === null ? <div className="thinking"><span></span><span></span><span></span><small>Reading your document…</small></div> : <><p className={item.failed ? 'answer-error' : ''}>{item.answer}</p>{item.sources?.length > 0 && <div className="sources"><button className="sources-toggle" onClick={() => setShowSources(!showSources)}><span><Files size={14} /> Sources <span className="source-count">{item.sources.length}</span></span><ChevronDown size={15} className={showSources ? '' : 'closed'} /></button>{showSources && <div className="source-list">{item.sources.map((source, sourceIndex) => <div className="source-card" key={source.chunk_id || sourceIndex}><div className="source-card-top"><span className="source-number">{sourceIndex + 1}</span><strong>{source.source || activeDoc.filename}</strong><span className="page-label">{source.page_number ? `Page ${source.page_number}` : 'Document'}</span></div><div className="source-meta">Excerpt {source.chunk_index !== null && source.chunk_index !== undefined ? `· section ${source.chunk_index + 1}` : ''} <span className="relevance"><Check size={11} /> {Math.round((source.relevance_score || 0) * 100)}% match</span></div></div>)}</div>}</div>}</>}</div></div></div>)}</div>}
              </div>
              {error && <div className="inline-alert"><span>{error}</span><button onClick={() => setError('')} aria-label="Dismiss"><X size={15} /></button></div>}
              {notice && <div className="inline-notice"><Check size={14} /> {notice}</div>}
              <form className="composer" onSubmit={(e) => { e.preventDefault(); ask() }}><textarea ref={promptRef} value={question} onChange={(e) => setQuestion(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); ask() } }} placeholder="Ask anything about this document…" rows={2} disabled={sending} /><div className="composer-bottom"><span><span className="composer-hint"><Sparkles size={13} /> Answers include source references</span><span className="key-hint">↵ to send · ⇧↵ for new line</span></span><button className="send-button" type="submit" disabled={!question.trim() || sending} aria-label="Send question">{sending ? <LoaderCircle className="spin" size={17} /> : <ArrowUp size={18} />}</button></div></form>
              <div className="chat-footnote"><ShieldCheck size={13} /> Your documents are private and only visible to you.</div>
            </div>
          </>}
          </>}
        </div>
      </main>
      <input className="hidden-input" ref={fileRef} type="file" accept="application/pdf,.pdf" onChange={(e) => uploadFiles(e.target.files)} />
    </div>
  )
}

// A child component receives data and callbacks through props. Keeping this
// empty/upload state separate makes the main component easier to navigate.
function EmptyState({ uploading, onUpload, onDrop }) {
  // Dragging is local to this component, so its state belongs here.
  const [dragging, setDragging] = useState(false)
  return <div className="empty-wrap"><div className={`empty-card ${dragging ? 'dragging' : ''}`} onDragOver={(e) => { e.preventDefault(); setDragging(true) }} onDragLeave={() => setDragging(false)} onDrop={(e) => { e.preventDefault(); setDragging(false); onDrop(e.dataTransfer.files) }}><div className="empty-icon"><FolderOpen size={25} /></div><span className="eyebrow">YOUR DOCUMENT WORKSPACE</span><h1>Understand Your Document Better </h1><p>Bring a PDF into your workspace. Ask questions, find key details, and get answers grounded in the original document.</p><button className="button button-primary" onClick={onUpload} disabled={uploading}>{uploading ? <LoaderCircle className="spin" size={17} /> : <Upload size={17} />}{uploading ? 'Processing document…' : 'Upload a PDF'}<ArrowRight size={15} /></button><div className="drop-hint">or drag and drop a PDF here</div><div className="empty-features"><span><Sparkles size={15} /> AI-powered answers</span><span><ShieldCheck size={15} /> Private by design</span></div></div><div className="empty-foot"><span><FileText size={15} /> PDF files only</span><span><ArrowDownToLine size={14} /> Your files stay in your workspace</span></div></div>
}

// Login/register UI is another component. Props connect its inputs and actions
// to state and handlers owned by App, which is the shared source of truth.
function AuthScreen({ authMode, setAuthMode, authEmail, setAuthEmail, password, setPassword, submitAuth, error, setError }) {
  return <div className="auth-page"><section className="auth-aside"><a className="brand brand-light" href="#home"><span className="brand-mark"><Files size={18} /></span><span>docLenseAi</span></a><div className="auth-hero"><span className="auth-kicker"><Sparkles size={14} /> DOCUMENT INTELLIGENCE</span><h1>Get to the<br />heart of every<br /><em>document.</em></h1><p>Your documents hold the answers. Find them faster with an AI workspace built for clarity.</p><div className="auth-quote"><div className="quote-mark">“</div><p>Everything I need to know, in one thoughtful conversation.</p><span>— A better way to work with documents</span></div></div><div className="auth-aside-foot"><span>Private by design</span><span>·</span><span>Made for clarity</span></div><div className="auth-orb orb-a"></div><div className="auth-orb orb-b"></div></section><section className="auth-main"><div className="auth-form-wrap"><div className="mobile-brand"><span className="brand-mark"><Files size={18} /></span> documind</div><div className="auth-heading"><span className="eyebrow">YOUR DOCUMENT WORKSPACE</span><h2>{authMode === 'login' ? 'Welcome back' : 'Create your account'}</h2><p>{authMode === 'login' ? 'Sign in to pick up where you left off.' : 'A clearer way to work with your documents starts here.'}</p></div><form className="auth-form" onSubmit={submitAuth}><label>Email address<input type="email" value={authEmail} onChange={(e) => setAuthEmail(e.target.value)} placeholder="you@company.com" autoComplete="email" required /></label><label>Password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="At least 8 characters" autoComplete={authMode === 'login' ? 'current-password' : 'new-password'} minLength={8} required /></label>{error && <div className="auth-error"><X size={15} />{error}</div>}<button className="button button-primary auth-submit" type="submit">{authMode === 'login' ? 'Sign in' : 'Create account'}<ArrowRight size={16} /></button></form><div className="auth-switch">{authMode === 'login' ? 'New to Documind?' : 'Already have an account?'} <button onClick={() => { setError(''); setAuthEmail(''); setPassword(''); setAuthMode(authMode === 'login' ? 'register' : 'login') }}>{authMode === 'login' ? 'Create an account' : 'Sign in'}</button></div><div className="auth-security"><ShieldCheck size={14} /> Your account and documents are private.</div></div><div className="auth-copyright">© 2026 DocLenseAi <span>·</span> Thoughtful tools for complex documents</div></section></div>
}

export default App
