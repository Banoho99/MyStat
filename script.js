paragraphs.forEach(p => {
	p.addEventListener('click', () =>{
		alert('Vous avez cliquer sur :"${p.textContent}"');
	});

});
