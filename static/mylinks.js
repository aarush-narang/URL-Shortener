window.addEventListener('load', function () {
    function createLinkElement(link, shortlink) {
        const linkscontainer = document.getElementById('container')
        const outerDiv = document.createElement('div')
        const innerDiv = document.createElement('div')
        const linkContainer = document.createElement('div')
        const long_link = document.createElement('a')
        const short_link = document.createElement('a')

        linkContainer.append(long_link, short_link)
        innerDiv.appendChild(linkContainer)
        outerDiv.appendChild(innerDiv)
        linkscontainer.appendChild(outerDiv)

        outerDiv.className = 'link-container-back'
        innerDiv.className = 'link-container-front'
        linkContainer.className = 'links-container'

        long_link.innerHTML = link.length < 28 ? link : link.slice(0, 29) + '...'
        long_link.onclick = () => window.open(link)
        long_link.id = 'llink'

        short_link.innerHTML = shortlink.split('/').reverse()[0]
        short_link.onclick = () => window.open(shortlink)
        short_link.id = 'slink'
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