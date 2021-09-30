const script = document.currentScript

window.addEventListener('load', function () {
    function createLinkElement(link, shortlink) {
        const domain = script.getAttribute('domain')
        const port = script.getAttribute('port')

        const linkscontainer = document.getElementById('container')
        const outerDiv = document.createElement('div')
        const innerDiv = document.createElement('div')
        const linkContainer = document.createElement('div')
        const long_link = document.createElement('a')
        const short_link = document.createElement('a')

        const copy_btn = document.createElement('button')
        const settings_btn = document.createElement('button')
        const settings_icon = document.createElement('i')

        const btns_container = document.createElement('div')
        btns_container.append(copy_btn, settings_btn)

        btns_container.id = 'btns-container'

        copy_btn.id = 'copy-btn'
        copy_btn.innerHTML = 'Copy Link'

        settings_btn.appendChild(settings_icon)
        settings_btn.id = 'settings-btn'
        settings_icon.className = 'fa fa-gear'

        

        linkContainer.append(long_link, short_link)
        innerDiv.append(linkContainer, btns_container)
        outerDiv.appendChild(innerDiv)
        linkscontainer.appendChild(outerDiv)

        outerDiv.className = 'link-container-back'
        innerDiv.className = 'link-container-front'
        linkContainer.className = 'links-container'

        long_link.innerHTML = link.length < 28 ? link : link.slice(0, 29) + '...'
        long_link.onclick = () => window.open(link)
        long_link.id = 'llink'

        short_link.innerHTML = `https://${domain}:${port}/${shortlink}`
        short_link.onclick = () => window.open(shortlink)
        short_link.id = 'slink'

        copy_btn.onclick = () => { // add modal or something that says copied
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
                range.moveToElementText(short_link);
                range.select().createTextRange();
                document.execCommand("copy");
            } else if (window.getSelection) {
                var range = document.createRange();
                range.selectNode(short_link);
                window.getSelection().addRange(range);
                document.execCommand("copy");
            }
            clearSelect()
        }
    }
    function getLinks() {
        const linksXHR = new XMLHttpRequest();
        linksXHR.addEventListener('load', function (res) {
            links = JSON.parse(res.target.responseText).links
            if (links === 'NO_LINKS') {
                return console.log('no links, put some html stuff here that says to them they have no links')
            }
            links.forEach(element => {
                createLinkElement(element.link, element.shortlink)
            });
        })
        linksXHR.addEventListener('error', function (resp) {
            
        })

        linksXHR.open('GET', '/links')
        linksXHR.send()
    }
    getLinks()
})