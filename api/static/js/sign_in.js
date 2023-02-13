window.addEventListener("load", function () {
    const sign_in_form = document.getElementById('sign-in-form')
    const token = document.getElementsByName('csrf_token') // CSRF Token for authorization
    const email = document.getElementById('email')
    const password = document.getElementById('password')
    const email_warning = document.getElementById('warning-message-email')
    const pass_warning = document.getElementById('warning-message-password')
    const general_warning = document.getElementById('warning-message')
    const show_pass = document.getElementById('pass-show')

    show_pass.onclick = () => {
        if(password.type === 'password') {
            show_pass.innerHTML = 'hide'
            password.type = 'text'
        } else {
            show_pass.innerHTML = 'show'
            password.type = 'password'
        }
    }

    function sendData() {
        const pwd = password.value
        const signinXHR = new XMLHttpRequest()
        signinXHR.addEventListener('load', (event) => {
            const resp = JSON.parse(event.target.response)
            if(resp.msg === 'INVALID_EMAIL' || resp.msg === 'INVALID_PASSWORD') {
                sign_in_form.reset()
                const old_email = email.value
                const old_password = password.value
                email.style.border = password.style.border = '1px solid red'
                email_warning.style.display = pass_warning.style.display = 'block'
                email_warning.innerHTML = pass_warning.innerHTML = 'Your email or password is incorrect.'
                const interval = setInterval(() => {
                    if(email.value != old_email || password.value != old_password) {
                        email.style.border = password.style.border = 'none'
                        email_warning.style.display = pass_warning.style.display = 'none'
                        email_warning.innerHTML = pass_warning.innerHTML = ''
                        clearInterval(interval)
                    }
                }, 100);
            } else if(resp.msg === 'LOGGED_IN') {
                return window.location = '/'
            }
        })
        signinXHR.addEventListener('error', (event) => {
            general_warning.style.display = 'block'
            general_warning.innerHTML = 'Oops! Something went wrong, try refreshing the page and try again.'
            return
        })

        signinXHR.open('POST', '/sign_in') // open the request
        signinXHR.setRequestHeader('X-CSRFToken', token[0].getAttribute('value')) // add header for csrf token
        signinXHR.send(JSON.stringify({ "email": email.value, "password": pwd }))
    }
    sign_in_form.addEventListener('submit', function (event) {
        event.preventDefault()
        const email_regex = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/

        if(!email_regex.test(email.value)) { // checks for valid email
            const old_email = email.value
            email.style.border = '1px solid red'
            email_warning.style.display = 'block'
            email_warning.innerHTML = 'Please enter a valid email.'
            const emailInterval = setInterval(() => {
                if(email.value != old_email) {
                    email.style.border = 'none'
                    email_warning.style.display = 'none'
                    email_warning.innerHTML = ''
                    clearInterval(emailInterval)
                }
            }, 100);
        } else if(password.value === ''){ // check if there is something in the password input
            const old_pass = password.value
            password.style.border = '1px solid red'
            pass_warning.style.display = 'block'
            pass_warning.innerHTML = 'Please enter a password.'
            const passInterval = setInterval(() => {
                if(password.value != old_pass) {
                    password.style.border = 'none'
                    pass_warning.style.display = 'none'
                    pass_warning.innerHTML = ''
                    clearInterval(passInterval)
                }
            }, 100);
        }
        else {
            sendData()
        }
    })
});