function toggleTheme(){
    document.body.classList.toggle('dark-mode');
    alert("Theme toggled!");
}

function confirmDelete(name){
    return confirm(`Are you sure you want to delete ${name}?`);
}

/*Carousel javascript*/

document.addEventListener("DOMContentLoaded", () => {
    let index = 0;
    const slides = document.querySelectorAll('.quote-slide');

    function showQuote() {
        slides.forEach((slide, i) => {
            slide.classList.remove('active');
        });

        slides[index].classList.add('active');
            index = (index + 1) % slides.length;
    }

    if (slides.length > 0){
        setInterval(showQuote, 3000);
    }
});