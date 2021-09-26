function getHeader() {
    if (script.getAttribute('user')) {
        const user_drop = document.getElementById('dropdown-container')
        user_drop.style.display = 'flex'
        
        // show dropdown with their email and dropdown includes "my links" and "logout"
    } else {
        document.getElementById('sign-in').style.display = 'block'
        document.getElementById('sign-up').style.display = 'block'
    }
}
window.addEventListener("load", function () { 
    getHeader()
    const sign_in_btn = document.getElementById('sign-in') // sign-in/sign-up buttons
    sign_in_btn.onclick = () => window.location = '/sign_in'
    const sign_up_btn = document.getElementById('sign-up')
    sign_up_btn.onclick = () => window.location = '/sign_up'

    document.addEventListener('click', event => {
        const isDropdownButton = event.target.matches('[data-dropdown-button]')
        if(!isDropdownButton && event.target.closest('[data-dropdown]') != null) return

        let currentDropdown
        if(isDropdownButton) {
            currentDropdown = event.target.closest('[data-dropdown]')
            currentDropdown.classList.toggle('active')
        }

        document.querySelectorAll('[data-dropdown].active').forEach(dropdown => {
            if(dropdown === currentDropdown) return
            dropdown.classList.remove('active')
        })
    })
    
    
    
    
})