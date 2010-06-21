// ==UserScript==
// @name MM IMDB add-on
// @description Add IMDB movie to you Movie Manager
// @include http*://*.imdb.com/title/*
// @include http*://imdb.com/title/*
// ==/UserScript==

(function() {

	var mmLocation = 'http://${c.parser.get('server:main', 'host') + ':' + c.parser.get('server:main', 'port')}';
	var link = "/movie/imdbAdd/";
	var id = 'tt'+location.href.replace(/[^\d+]+/g, '');
	
	var navbar, newElement;
	titleEl = document.getElementById('title-media-strip');

//Popup
	popupElement = document.createElement('span');
	popupElement.id = 'mmPopup'
	popupElement.style.cssFloat = 'left'
	popupElement.style.marginRight = '10px'
	var inHTML = '<span style="background:#f5f5f5; z-index: 99999; display: block; padding:10px 20px;">';
		inHTML += '<iframe src="'+mmLocation + link + id + '/" style="margin:15px 10px; height:60px; width:140px; overflow:hidden; border:none;"></iframe>'
		inHTML += '</span>'
	popupElement.innerHTML = inHTML
	
	var p = titleEl.getElementsByTagName('table')[0]
	p.parentNode.insertBefore(popupElement, p);

})();