import React from 'react';
import '../style/authorization.css';

export const Authorization = () => {
    const handleAuth = (e) => {
        e.preventDefault();

        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;
        fetch('http://192.168.0.105:8000/authorization', {
            method: 'POST',
            //mode: 'no-cors',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({email: email, password: password})
        }).then(response => response.json()).then(data => {
            if(data['success']){
                document.cookie = `bearer=${data['token']}; path=/;`
                alert("Авторизация прошла успешно!")
                console.log(document.cookie)
                window.location.href = '/Main'
            }
            else{
                alert(data['message'])
                console.log(data['message'])
            }
        })
    }
  return (
    <div> 
        <h2>Authorization</h2>
        <form id="authorization_form">
            <label htmlFor="email">Email</label>
            <input type="email" id="email" name="email" required></input>
            <label htmlFor="password">Password</label>
            <input type="password" id="password" name="password" required></input>
            <button type="submit" onClick={handleAuth}>Authorization</button>
        </form>
    </div>
  )
}
export default Authorization
