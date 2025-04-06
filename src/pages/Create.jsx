import React, { useState } from 'react'
import { useEffect } from 'react'
import "../style/Create.css"

const Create = () => {
//   useEffect(() => {
//     ParseProjects()
// }, [])
  const [Opts, setOpts] = useState('')

    //Создание чата
  // const ParseProjects = () => {
  //   fetch('http://localhost:8000/projects/list', {
  //       method: 'GET',
  //       mode: 'no-cors',
  //       headers: {
  //           'Content-Type': 'application/json',
  //       }
  //       }).then(response => response.json()).then(data => {
  //           if (data.length > 0) {
  //               setOpts(data)
  //           }
  //   })
  // }
  return (
    <div className='bg'>
  
      <div className='main'>
        <h1 className='name'></h1>
        <span></span>
          <div className='inp_main'>
           <input type="text" name="" id="" className='inp'/>
        
           {/*Тут логика будет выбора проектов. На запуске парсятся проекты с сайта (GET) и кидаются как опции в этот селект*/}
          <select className="sel_main" id="">
             {/* {Opts.map((opt) => {
              return(
                <option value={opt.id}>{opt.id.name}</option>
              )
             })} */}
          </select>
          </div>
        </div>
    </div>
  )
}

export default Create
