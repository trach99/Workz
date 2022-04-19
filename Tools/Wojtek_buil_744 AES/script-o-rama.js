reposition = function() {
  var e = document.getElementById("section_middle");
  var used = document.getElementById("section_top").clientHeight +
      document.getElementById("section_bottom").clientHeight;
  e.style.height = Math.max(0, (document.body.clientHeight - used - 20))+ "px";
  e.style.width = Math.max(0, (document.body.clientWidth - 18)) + "px";
}

window.onload = reposition;
window.onresize = reposition;
