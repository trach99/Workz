function toggle(elementId) {
	var e = document.getElementById(elementId);
	if (e.style.display != 'inline')
		e.style.display = 'inline';
	else
		e.style.display = 'none';
}

