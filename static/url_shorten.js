const script = document.currentScript
const domain = `http://${script.getAttribute('domain')}:${script.getAttribute('port')}/`

function copy_short_link() {
    const copyText = document.querySelector("#link");
    copyText.select();
    document.execCommand("copy");
}

window.addEventListener("load", function () {
    const form = document.getElementById("link-form")
    const input = document.getElementById("link")
    const link_submit_button = document.getElementById('link-submit')
    const warning_message = document.getElementById('warning-message')
    let open_btn
    function warn(respMsg) { // function that loads the warn/rate limit
        old_value = input.value
        input.style.border = 'thin solid red'

        warning_message.innerHTML = respMsg

        const warning_interval = setInterval(() => {
            if(input.value != old_value) {
                input.style.border = 'none'
                warning_message.innerHTML = ''
                clearInterval(warning_interval)
            }
        }, 100);
    }
    function check_input_value(short_link) { // checks to see if the input value was changed
        const input_check = setInterval(() => { // make the "copy link" button and "open link" buttons disappear and only show the "shorten" button
            if (input.value != short_link) {
                link_submit_button.value = 'Shorten'
                link_submit_button.type = 'submit'
                link_submit_button.style.width = '609px'
                open_btn.style.width = '0px'
                open_btn.style.display = 'none'
                clearInterval(input_check)
            }
        }, 100);
    }
    function sendData(invalid=false, msg='') {
        if(invalid) {
            return warn(msg)
        }
        const XHR = new XMLHttpRequest();
        XHR.addEventListener("load", function (event) { // when the response comes back
            resp = JSON.parse(event.target.responseText)
            if (resp.error) { // check if the person is ratelimited
                return warn(resp.msg)
            }
            input.value = `${domain}${resp.short_link}` // otherwise edit the input value to show the new shortened link
            check_input_value(`${domain}${resp.short_link}`) // create an interval to check if the input is changed
            link_submit_button.value = 'Copy Link' // change shorten button to copy button
            link_submit_button.type = 'button'
            link_submit_button.style.width = '300px'

            // make the "open link" btn appear and will open the link when clicked
            open_btn = document.getElementById('link-open')
            open_btn.style.display = 'block'
            open_btn.style.width = '302px'
            open_btn.onclick = () => window.open(input.value)

            document.querySelector("#link-submit").addEventListener("click", copy_short_link);
        });
        XHR.addEventListener("error", function (event) { // if error happens on backend
            link_input = document.getElementById('link')
            old_value = link_input.value
            link_input.style.border = 'thin solid red'

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
        IP_XHR.addEventListener('load', function (event) { // load the response from getting the ip (for ratelimiting)
            IP = JSON.parse(event.target.responseText).ip

            XHR.open("POST", "/url_shorten");
            XHR.send(JSON.stringify({ "link": input.value, 'ip': IP }));
        })
        IP_XHR.open('GET', 'https://api.ipify.org?format=json');
        IP_XHR.send();
    }
    
    form.addEventListener("submit", function (event) { // when "Shorten" button is clicked this will trigger
        event.preventDefault();
        const link_regex_1 = /(?!www\.)[a-zA-Z0-9._]{2,256}\.[a-z0-9:]{2,6}([-a-zA-Z0-9._]*)/g  // google.com
        const link_regex_2 = /(www\.)[a-zA-Z0-9._]{2,256}\.[a-z0-9:]{2,6}([-a-zA-Z0-9._]*)/g  // www.google.com
        const link_regex_3 = /((http|https):\/\/)(?!www\.)[a-zA-Z0-9._]{2,256}\.[a-z0-9:]{2,6}([-a-zA-Z0-9._]*)/g  // https://google.com
        const link_regex_4 = /((http|https):\/\/)(www\.)[a-zA-Z0-9._]{2,256}\.[a-z0-9:]{2,6}([-a-zA-Z0-9._]*)/g  // https://www.google.com
        if (input.value === '' || (!input.value.match(link_regex_1) && !input.value.match(link_regex_2) && !input.value.match(link_regex_3) && !input.value.match(link_regex_4))) {
            return sendData(true, 'Please enter a valid URL!');
        } else if(input.value.match(/((http:\/\/)?10\.18\.84\.212:3000\/)(.+)/g)) {
            return sendData(true, 'That is already a shortened link!')
        }
        return sendData();
    });
});