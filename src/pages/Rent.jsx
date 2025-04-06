import React from 'react'
import '../style/Rent.css'
const Rent = () => {
  return (
    <div className='bg2'>
      <div className='rentselector'>
        <select className='filter' name="" id="">
            <option value="1">оборудование</option>
            <option value="2">сервисы</option>
            <option value="3">стартапы</option>
        </select>
        <button className='lilbtn'>найти</button>
      </div>
      <div className='stuff'>
        {/* Тут парсятся объявления в зависимости от фильтра. Ниче тут не надо в этом диве будто бы */}
      </div>
    </div>
  )
}

export default Rent
