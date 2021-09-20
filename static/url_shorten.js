const domain = 'http://127.0.0.1:5000/'
function copy_short_link() {
    const copyText = document.querySelector("#link");
    copyText.select();
    document.execCommand("copy");
}

window.addEventListener("load", function () {
    function sendData() {
        const XHR = new XMLHttpRequest();
        XHR.addEventListener("load", function (event) {
            resp = JSON.parse(event.target.responseText)
            if (resp.valid === 'invalidURL') {
                link_input = document.getElementById('link')
                old_value = link_input.value
                link_input.style.border = 'thin solid red'

                warning_message = document.getElementById('warning-message')
                warning_message.innerHTML = resp.msg

                const warning_interval = setInterval(() => {
                    if(link_input.value != old_value) {
                        link_input.style.border = 'none'
                        warning_message.innerHTML = ''
                        clearInterval(warning_interval)
                    }
                }, 100);
            } else {
                input.value = `${domain}${resp.short_link}`
                check_input_value(`${domain}${resp.short_link}`)
                link_submit_button.value = 'Copy'
                link_submit_button.type = 'button'

                document.querySelector("#link-submit").addEventListener("click", copy_short_link);
            }
        });
        XHR.addEventListener("error", function (event) {
            alert(`Oops! Something went wrong.`);
        });
        XHR.open("POST", "/url_shorten");
        XHR.send(JSON.stringify({ "link": input.value }));
    }
    function check_input_value(short_link) {
        const input_check = setInterval(() => {
            if (input.value != short_link) {
                link_submit_button.value = 'Shorten'
                link_submit_button.type = 'submit'
                clearInterval(input_check)
            }
        }, 100);
    }
    const form = document.getElementById("link-form")
    const input = document.getElementById("link")
    const link_submit_button = document.getElementById('link-submit')
    form.addEventListener("submit", function (event) {
        event.preventDefault();
        sendData();
    });
});