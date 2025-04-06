import React from 'react'

export const Registration = () => {
  const handleReg = (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const first_name = document.getElementById("first_name").value;
    const last_name = document.getElementById("last_name").value;
    fetch("http://192.168.0.105:8000/registration", {
        method: "POST",
        mode: 'no-cors',
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            email: email,
            password: password,
            first_name: first_name,
            last_name: last_name
        })
    }).then(response => response.json()).then(data => {
        if(data['success']){
            document.cookie = `bearer=${data['token']}; path=/;`
            alert("Регистрация прошла успешно!")
            console.log(document.cookie)
            window.location.reload()
        }
        else{
            alert(data['message'])
            console.log(data['message'])
        }
    }
    )}
    return (
    <div>Registration
        <form id="registration_form">
            <label htmlFor="email">Email</label>
            <input type="email" id="email" name="email" required></input>
            <label htmlFor="password">Password</label>
            <input type="password" id="password" name="password" required></input>
            <label htmlFor="first_name">First name</label>
            <input type="text" id="first_name" name="first_name" required></input>
            <label htmlFor="last_name">Last name</label>
            <input type="text" id="last_name" name="last_name" required></input>
            <button type="submit" onClick={handleReg}>Registration</button>
        </form>
    </div>
  )
}
export default Registration