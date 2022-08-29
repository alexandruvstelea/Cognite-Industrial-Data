const template = document.createElement('template');

template.innerHTML = `
<div class="navigation_bar">
<div class="container">
    <a class="logo" href="/FrontEnd/HTML/index.html">Cognite Industrial<span> Data</span></a>
    <nav>
        <ul class="main_navigation_bar">
            <li class="current_page">
                <a class="home-button" href="/FrontEnd/HTML/index.html">Home</a>
            </li>
            <li><a class="assets-button" href="/FrontEnd/HTML/assets.html">Assets</a></li>
        </ul>

        <ul class="secondary_navigation_bar">
            <li class="aboutButton"><a href="#">About project</a></li>
        </ul>
    </nav>
</div>
</div>
`;

document.body.appendChild(template.content);