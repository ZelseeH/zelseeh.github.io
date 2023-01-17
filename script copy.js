var slideIndex = 1;
pokaDivs(slideIndex);

function minusDivs(n) {
  pokaDivs(slideIndex += n);
}

function pokaDivs(n) {
  var i;
  var x = document.getElementsByClassName("slajderson");
  if (n > x.length) {slideIndex = 1}
  if (n < 1) {slideIndex = x.length}
  for (i = 0; i < x.length; i++) {
    x[i].style.display = "none";  
  }
  x[slideIndex-1].style.display = "block";  
}