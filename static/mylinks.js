const script = document.currentScript

window.addEventListener('load', function () {
    function createLinkElement(link, shortlink) {
        if(link === 'NO_LINKS') {
            const linkscontainer = document.getElementById('container')
            const no_links_text = document.createElement('p')
            no_links_text.id = 'no-links'
            no_links_text.innerHTML = 'Oops, It looks like you have no links. Return home and get shortening!'
            linkscontainer.appendChild(no_links_text)
            return
        }
        const domain = script.getAttribute('domain')
        const port = script.getAttribute('port')

        const linkscontainer = document.getElementById('container')
        const linkTemplate = document.querySelector('template')

        const templatecontent = linkTemplate.content.cloneNode(true)

        const buttons = templatecontent.querySelectorAll('button')
        const links = templatecontent.querySelectorAll('a')
        
        links[0].innerHTML = link.length < 28 ? link : link.slice(0, 29) + '...' // set the values for the long link
        links[0].onclick = () => window.open(link)
        
        
        links[1].innerHTML = `https://${domain}:${port}/${shortlink}` // set values for short link
        links[1].onclick = () => window.open(shortlink)

        buttons[0].onclick = () => { // copy link button
            function clearSelect() {
                if (window.getSelection) {
                    if (window.getSelection().empty) {
                        window.getSelection().empty();
                    } else if (window.getSelection().removeAllRanges) {
                        window.getSelection().removeAllRanges();
                    }
                } else if (document.selection) {
                    document.selection.empty();
                }
            }
            clearSelect()
            if (document.selection) {
                var range = document.body.createTextRange();
                range.moveToElementText(links[1]);
                range.select().createTextRange();
                document.execCommand("copy");
            } else if (window.getSelection) {
                var range = document.createRange();
                range.selectNode(links[1]);
                window.getSelection().addRange(range);
                document.execCommand("copy");
            }
            clearSelect()

            // change color of button to show it was copied
            buttons[0].style.backgroundColor = 'rgb(106, 222, 170)' 
            buttons[0].innerHTML = 'Copied!'
            buttons[0].style.color = 'black'
            setTimeout(() => {
                buttons[0].innerHTML = 'Copy Link'
                buttons[0].style.backgroundColor = ''
                buttons[0].style.color = ''
            }, 3000);
        }

        buttons[1].title = `Delete https://${domain}:${port}/${shortlink}`; // delete link button
        buttons[1].onclick = () => { // delete link button
            deletelink(link, shortlink)
        }

        linkscontainer.appendChild(templatecontent)
    }
    function deletelink(link, shortlink) {
        const deletelinkXHR = new XMLHttpRequest()
        deletelinkXHR.addEventListener('load', function (res) {
            window.location.reload()
        })
        deletelinkXHR.addEventListener('error', function () {
            console.log('error')
        })
        const token = document.getElementsByName('csrf_token') // CSRF Token for authorization
        deletelinkXHR.open('DELETE', '/deletelink')
        deletelinkXHR.setRequestHeader('X-CSRFToken', token[0].getAttribute('value')) // add header for csrf token
        deletelinkXHR.send(JSON.stringify({ link, shortlink }))
    }
    function getLinks() {
        const linksXHR = new XMLHttpRequest();
        linksXHR.addEventListener('load', function (res) {
            links = JSON.parse(res.target.responseText).links
            if (links.length === 0) {
                return createLinkElement('NO_LINKS', null)
            } else {
                const total_links_display = document.getElementById('total-links')
                total_links_display.innerHTML = `${links.length}/200 Links Used`
                links.forEach(element => {
                    createLinkElement(element.link, element.shortlink)
                });
            }
        })
        linksXHR.addEventListener('error', function (resp) {
            console.log('error')
        })
        linksXHR.open('GET', '/getlinks')
        linksXHR.send()
    }
    getLinks()
})