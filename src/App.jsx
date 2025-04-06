import { useState } from 'react'
import './App.css'
import Create from './pages/Create'
import Main from './pages/main'
import Navbar from './components/Navbar'
import Rent from './pages/Rent'
//ТУТ ТОЖЕ ИМПОРТЫ РУТОВ
import {Route, Routes} from 'react-router-dom'
import { Navigate } from 'react-router'
import Authorization from './pages/Authorization'
import Registration from './pages/Registration'
function App() {
//ТУТ БУДЕТ ПРОВЕРКА НА АВТОРИЗАЦИЮ
//<Route path='/Homepage' element= {AuthUser ? <HomePage/> : <Navigate to="/Authorization"/>} />
  return (
    <>
      <Navbar/>
      <Routes>/
        <Route path="/Registration" element={<Registration/>}/>
        <Route path="/Authorization" element={<Authorization/>}/> {/* AuthUser - переменная с проверкой на авторизацию */}
        <Route path="/Create" element={<Create/>}/>
        <Route path="/Main" element={<Main/>}/>
        <Route path="/Rent" element={<Rent/>}/>
      </Routes>
      
    </>
  )
}

export default App
