// Menu responsive
document.querySelector('.menu-toggle').addEventListener('click',()=>{
    document.querySelector('nav').classList.toggle('open');
});

// Scroll lisse
Array.from(document.querySelectorAll('nav a')).forEach(link=>{
    link.addEventListener('click',e=>{
        e.preventDefault();
        document.querySelector(link.getAttribute('href')).scrollIntoView({behavior:'smooth'});
    });
});