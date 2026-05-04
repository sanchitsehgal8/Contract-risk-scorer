import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import App from './App'
import { ContractProvider } from './store/ContractContext'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <ContractProvider>
        <App />
        <Toaster position="top-right" />
      </ContractProvider>
    </BrowserRouter>
  </React.StrictMode>,
)
