// Simple JS for carousel, hamburger and mini slider
document.addEventListener('DOMContentLoaded', function(){
  // Hamburger
  const hamburger = document.getElementById('hamburger');
  const sidebar = document.getElementById('sidebar');
  hamburger.addEventListener('click', ()=> {
    if(sidebar.style.display === 'block'){ sidebar.style.display = 'none'; }
    else { sidebar.style.display = 'block'; sidebar.style.position='absolute'; sidebar.style.zIndex= '20'; sidebar.style.left='10px'; sidebar.style.top='60px'; sidebar.style.width='80%'}
  });

  // Carousel
  const slides = document.querySelectorAll('.carousel .slides img');
  const dotsContainer = document.getElementById('dots');
  let idx = 0;
  slides.forEach((s,i)=> {
    const btn = document.createElement('button');
    btn.addEventListener('click', ()=> goTo(i));
    dotsContainer.appendChild(btn);
  });
  function show(n){
    slides.forEach(s=> s.classList.remove('active'));
    slides[n].classList.add('active');
  }
  function goTo(n){ idx = n; show(idx); }
  function next(){ idx = (idx+1) % slides.length; show(idx); }
  show(idx);
  setInterval(next, 4000);

  // mini slider
  const images = ['assets/thumb1.svg','assets/thumb2.svg','assets/thumb3.svg'];
  let m = 0;
  const miniImg = document.getElementById('mini-img');
  document.getElementById('prev').addEventListener('click', ()=> {
    m = (m-1+images.length)%images.length; miniImg.src = images[m];
  });
  document.getElementById('next').addEventListener('click', ()=> {
    m = (m+1)%images.length; miniImg.src = images[m];
  });
});
