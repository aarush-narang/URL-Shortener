const currentscript = document.currentScript
function getHeader() {
    if (currentscript.getAttribute('user')) {
        const user_drop = document.getElementById('dropdown-container')
        user_drop.style.display = 'flex'
        // show dropdown
    } else {
        document.getElementById('sign-in').style.display = 'block'
        document.getElementById('sign-up').style.display = 'block'
    }
}
window.addEventListener("load", function () { 
    getHeader()
    const sign_in_btn = document.getElementById('sign-in') // sign-in/sign-up buttons
    if(sign_in_btn) sign_in_btn.onclick = () => window.location = '/sign_in'
    const sign_up_btn = document.getElementById('sign-up')
    if(sign_up_btn) sign_up_btn.onclick = () => window.location = '/sign_up'

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