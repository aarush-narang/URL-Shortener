window.addEventListener("load", function () {
    function startPasswordCheck(input_type) {
        const pass_total_msg = document.getElementById('msg-total')
        const pass_lower_msg = document.getElementById('msg-lower')
        const pass_upper_msg = document.getElementById('msg-upper')
        const pass_number_msg = document.getElementById('msg-number')
        const pass_special_msg = document.getElementById('msg-special')
        const password_total = /^.{8,}$/
        const password_lowwercase = /(?=(.*[a-z]){3,})/
        const password_uppercase = /(?=(.*[A-Z]){2,})/
        const password_numbers = /(?=(.*[0-9]){2,})/
        const password_special = /(?=(.*[!@#$%^&*()\-__+.]){1,})/
        let password_reqs
        function startPasswordInterval(input) {
            password_reqs = setInterval(() => {
                if(password_total.test(input.value)) {
                    pass_total_msg.style.color = 'rgb(91, 219, 144)'
                } else {
                    pass_total_msg.style.color = 'rgb(201, 87, 87)'
                }
                if(password_lowwercase.test(input.value)) {
                    pass_lower_msg.style.color = 'rgb(91, 219, 144)'
                } else {
                    pass_lower_msg.style.color = 'rgb(201, 87, 87)'
                }
                if(password_uppercase.test(input.value)) {
                    pass_upper_msg.style.color = 'rgb(91, 219, 144)'
                } else {
                    pass_upper_msg.style.color = 'rgb(201, 87, 87)'
                }
                if(password_numbers.test(input.value)) {
                    pass_number_msg.style.color = 'rgb(91, 219, 144)'
                } else {
                    pass_number_msg.style.color = 'rgb(201, 87, 87)'
                }
    
                if(password_special.test(input.value)) {
                    pass_special_msg.style.color = 'rgb(91, 219, 144)'
                } else {
                    pass_special_msg.style.color = 'rgb(201, 87, 87)'
                }
            }, 100);
        }
        startPasswordInterval(input_type)
    }
    const sign_up_form = document.getElementById('sign-up-form')
    const token = document.getElementsByName('csrf_token') // CSRF Token for authorization
    const email = document.getElementById('email') // email input
    const password = document.getElementById('password') // password input
    const verif_pass = document.getElementById('verify-password')  // verify password input
    const username = document.getElementById('username')
    // warning messages
    const email_warning = document.getElementById('warning-message-email')
    const pass_warning = document.getElementById('warning-message-password')
    const username_warning = document.getElementById('warning-message-username')
    const verif_pass_warning = document.getElementById('warning-message-verify-password')
    const general_warning = document.getElementById('warning-message')
    // show password text
    const show_pass = document.getElementById('pass-show')
    const verif_show_pass = document.getElementById('v-pass-show')

    // setup events for click on the show password button
    show_pass.onclick = () => {
        if(password.type === 'password') {
            show_pass.innerHTML = 'hide'
            password.type = 'text'
        } else {
            show_pass.innerHTML = 'show'
            password.type = 'password'
        }
    }
    verif_show_pass.onclick = () => {
        if(verif_pass.type === 'password') {
            verif_show_pass.innerHTML = 'hide'
            verif_pass.type = 'text'
        } else {
            verif_show_pass.innerHTML = 'show'
            verif_pass.type = 'password'
        }
    }

    // when they go to the password input, show the grid of requirements for the password
    password.addEventListener('focus', function (event) {
        const pass_check_grid = document.getElementById('password-requirements')
        pass_check_grid.style.display = 'grid'
        startPasswordCheck(password)
    })
    
    // send the request to create the account
    function sendData() {
        const encrypted_pass = window.shajs('sha512').update(password.value).digest('hex')
        const signupXHR = new XMLHttpRequest()
        signupXHR.addEventListener('load', (event) => {
            const resp = JSON.parse(event.target.response)
            if(resp.msg === 'EXISTING_EMAIL') {
                sign_up_form.reset()
                old_email = email.value
                email.style.border = '1px solid red'
                email_warning.style.display = 'block'
                email_warning.innerHTML = 'An account with this email already exists.'
                const emailInterval = setInterval(() => {
                    if(email.value != old_email) {
                        email.style.border = 'none'
                        email_warning.style.display = 'none'
                        email_warning.innerHTML = ''
                        clearInterval(emailInterval)
                    }
                }, 100);
            } else if(resp.msg === 'EXISTING_USERNAME') {
                sign_up_form.reset()
                old_username = username.value
                username.style.border = '1px solid red'
                username_warning.style.display = 'block'
                username_warning.innerHTML = 'An account with this username already exists.'
                const usernameInterval = setInterval(() => {
                    if(username.value != old_username) {
                        username.style.border = 'none'
                        username_warning.style.display = 'none'
                        username_warning.innerHTML = ''
                        clearInterval(usernameInterval)
                    }
                }, 100);
            } else if(resp.msg === 'INVALID_EMAIL') {
                sign_up_form.reset()
                old_email = email.value
                email.style.border = '1px solid red'
                email_warning.style.display = 'block'
                email_warning.innerHTML = 'Please enter a valid email..'
                const emailInterval = setInterval(() => {
                    if(email.value != old_email) {
                        email.style.border = 'none'
                        email_warning.style.display = 'none'
                        email_warning.innerHTML = ''
                        clearInterval(emailInterval)
                    }
                }, 100);
            } else if(resp.msg === 'INVALID_USERNAME') {
                sign_up_form.reset()
                old_username = username.value
                username.style.border = '1px solid red'
                username_warning.style.display = 'block'
                username_warning.innerHTML = 'Please enter a valid username.'
                const usernameInterval = setInterval(() => {
                    if(username.value != old_username) {
                        username.style.border = 'none'
                        username_warning.style.display = 'none'
                        username_warning.innerHTML = ''
                        clearInterval(usernameInterval)
                    }
                }, 100);
            } else if(resp.msg === 'SIGNED_UP') {
                const signinXHR = new XMLHttpRequest()
                signinXHR.addEventListener('load', (event) => {
                    return window.location = '/home'
                })
                signinXHR.addEventListener('error', (event) => {
                    console.log('error')
                })

                signinXHR.open('POST', '/sign_in')
                signinXHR.setRequestHeader('X-CSRFToken', token[0].getAttribute('value'))
                signinXHR.send(JSON.stringify({ "email": email.value, "password": encrypted_pass }))
            }
        })
        signupXHR.addEventListener('error', (event) => {
            general_warning.style.display = 'block'
            general_warning.innerHTML = 'Oops! Something went wrong, try refreshing the page and try again.'
            return
        })

        signupXHR.open('POST', '/sign_up')
        signupXHR.setRequestHeader('X-CSRFToken', token[0].getAttribute('value'))
        signupXHR.send(JSON.stringify({ "username": username.value, "email": email.value, "password": encrypted_pass }))
    }
    // when the form is submitted go through these checks
    sign_up_form.addEventListener('submit', function (event) {
        event.preventDefault()
        const email_regex = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
        const password_regex = /^(?! )(?=(.*[a-z]){3,})(?=(.*[A-Z]){2,})(?=(.*[0-9]){2,})(?=(.*[!@#$%^&*()\-__+.]){1,}).{8,}(?<! )$/
        const username_regex = /^[a-zA-Z0-9]{1,20}$/

        if(!username_regex.test(username.value)) {
            old_username = username.value
            username.style.border = '1px solid red'
            username_warning.style.display = 'block'
            username_warning.innerHTML = 'Please enter a valid username.'
            const usernameInterval = setInterval(() => {
                if(username.value != old_username) {
                    username.style.border = 'none'
                    username_warning.style.display = 'none'
                    username_warning.innerHTML = ''
                    clearInterval(usernameInterval)
                }
            }, 100);
        }
        else if(!email_regex.test(email.value)) { // checks for valid email
            old_email = email.value
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
        } else if(!password_regex.test(password.value) || password.value.includes(' ')) { //check for valid password
            old_password = password.value
            password.style.border = '1px solid red'
            pass_warning.style.display = 'block'
            pass_warning.innerHTML = 'Please enter a valid password.'
            const passInterval = setInterval(() => {
                if(password.value != old_password) {
                    password.style.border = 'none'
                    pass_warning.style.display = 'none'
                    pass_warning.innerHTML = ''
                    clearInterval(passInterval)
                }
            }, 100);
        } else if(verif_pass.value !== password.value){ // check if passwords match
            old_password = verif_pass.value
            verif_pass.style.border = '1px solid red'
            verif_pass_warning.style.display = 'block'
            verif_pass_warning.innerHTML = 'Your passwords don\'t match.'
            const verifPassInterval = setInterval(() => {
                if(verif_pass.value != old_password) {
                    verif_pass.style.border = 'none'
                    verif_pass_warning.style.display = 'none'
                    verif_pass_warning.innerHTML = ''
                    clearInterval(verifPassInterval)
                }
            }, 100);
        }
        else {
            sendData()
        }
    })
});