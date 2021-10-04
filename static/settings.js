window.addEventListener('load', () => {
    const password_show = document.getElementById('show-pass-n')
    const password_show_verif = document.getElementById('show-pass-v')

    const password_input = document.getElementById('password-input')
    const password_input_verif = document.getElementById('v-password-input')

    password_show.onclick = () => {
        if(password_input.type === 'password') {
            password_show.innerHTML = 'hide'
            password_input.type = 'text'
        } else {
            password_show.innerHTML = 'show'
            password_input.type = 'password'
        }
    }
    password_show_verif.onclick = () => {
        if(password_input_verif.type === 'password') {
            password_show_verif.innerHTML = 'hide'
            password_input_verif.type = 'text'
        } else {
            password_show_verif.innerHTML = 'show'
            password_input_verif.type = 'password'
        }
    }
})
