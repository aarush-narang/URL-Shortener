const domain = 'http://127.0.0.1:5000/'
function copy_short_link() {
    const copyText = document.querySelector("#link");
    copyText.select();
    document.execCommand("copy");
}

window.addEventListener("load", function () {
    function warn(respMsg) {
        link_input = document.getElementById('link')
        old_value = link_input.value
        link_input.style.border = 'thin solid red'

        warning_message = document.getElementById('warning-message')
        warning_message.innerHTML = respMsg

        const warning_interval = setInterval(() => {
            if(link_input.value != old_value) {
                link_input.style.border = 'none'
                warning_message.innerHTML = ''
                clearInterval(warning_interval)
            }
        }, 100);
    }
    function sendData(invalid=false, msg='') {
        if(invalid) {
            return warn(msg)
        }
        const XHR = new XMLHttpRequest();
        XHR.addEventListener("load", function (event) {
            resp = JSON.parse(event.target.responseText)
            if (resp.valid === 'invalidURL') {
                return warn(resp.msg)
            }
            input.value = `${domain}${resp.short_link}`
            check_input_value(`${domain}${resp.short_link}`)
            link_submit_button.value = 'Copy'
            link_submit_button.type = 'button'

            document.querySelector("#link-submit").addEventListener("click", copy_short_link);
        });
        XHR.addEventListener("error", function (event) {
            link_input = document.getElementById('link')
            old_value = link_input.value
            link_input.style.border = 'thin solid red'

            warning_message = document.getElementById('warning-message')
            warning_message.innerHTML = 'Oops! Something went wrong, please try again.'

            const warning_interval = setInterval(() => {
                if(link_input.value != old_value) {
                    link_input.style.border = 'none'
                    warning_message.innerHTML = ''
                    clearInterval(warning_interval)
                }
            }, 100);
        });

        const IP_XHR = new XMLHttpRequest();
        IP_XHR.addEventListener('load', function (event) {
            IP = JSON.parse(event.target.responseText).ip

            XHR.open("POST", "/url_shorten");
            XHR.send(JSON.stringify({ "link": input.value, 'ip': IP }));
        })
        IP_XHR.open('GET', 'https://api.ipify.org?format=json');
        IP_XHR.send();
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
        const link_regex_1 = /(?!www\.)[a-zA-Z0-9._]{2,256}\.[a-z0-9:]{2,6}([-a-zA-Z0-9._]*)/g  // google.com
        const link_regex_2 = /(www\.)[a-zA-Z0-9._]{2,256}\.[a-z0-9:]{2,6}([-a-zA-Z0-9._]*)/g  // www.google.com
        const link_regex_3 = /((http|https):\/\/)(?!www\.)[a-zA-Z0-9._]{2,256}\.[a-z0-9:]{2,6}([-a-zA-Z0-9._]*)/g  // https://google.com
        const link_regex_4 = /((http|https):\/\/)(www\.)[a-zA-Z0-9._]{2,256}\.[a-z0-9:]{2,6}([-a-zA-Z0-9._]*)/g  // https://www.google.com
        if (input.value === '' || (!input.value.match(link_regex_1) && !input.value.match(link_regex_2) && !input.value.match(link_regex_3) && !input.value.match(link_regex_4))) {
            return sendData(true, 'Please enter a valid URL!');
        } else if(input.value.match(/((http:\/\/)?127\.0\.0\.1:5000\/)(.+)/g)) {
            return sendData(true, 'That is already a shortened link!')
        }
        sendData();
    });
});