// ==UserScript==
// @name 		MM IMDB add-on
// @description Add IMDB movie to you Movie Manager
// @include		http*://*.imdb.com/title/tt*
// @include		http*://imdb.com/title/tt*
// ==/UserScript==

function create() {
	switch (arguments.length) {
	case 1:
		var A = document.createTextNode(arguments[0]);
		break;
	default:
		var A = document.createElement(arguments[0]), B = arguments[1];
		for ( var b in B) {
			if (b.indexOf("on") == 0)
				A.addEventListener(b.substring(2), B[b], false);
			else if (",style,accesskey,id,name,src,href,which".indexOf(","
					+ b.toLowerCase()) != -1)
				A.setAttribute(b, B[b]);
			else
				A[b] = B[b];
		}
		for ( var i = 2, len = arguments.length; i < len; ++i)
			A.appendChild(arguments[i]);
	}
	return A;
}

if (typeof GM_addStyle == 'undefined')
	GM_addStyle = function(css) {
		var head = document.getElementsByTagName('head')[0], style = document
				.createElement('style');
		if (!head) {
			return
		}
		style.type = 'text/css';
		style.textContent = css;
		head.appendChild(style);
	}

// Styles
GM_addStyle('\
	#mmPopup { font-size:15px; width:170px; float:left; margin: 1px 10px 0 0; display: block; background:#f5f5f5; } \
	#mmPopup strong { background:#fff; display:block; } \
	#mmPopup a { text-align:center; text-decoration:none; color: #000; display:block; height:30px; width:170px; padding:30px 0; } \
	#mmPopup a img { vertical-align: middle; } \
	#mmPopup a:hover { color:#000; } \
	#mmPopup iframe{ height:90px; width:170px; overflow:hidden; border:none; } \
')

var mmLocation = 'http://${c.host}';
var link = "/movie/imdbAdd/";
var id = 'tt' + location.href.replace(/[^\d+]+/g, '');
var img = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAZCAYAAABQDyyRAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAA+9JREFUeNrMVklIXFkUPVWWY5cDccIpMQ444YCi7UJ3KrpUxAkURRAFW6GdMCI0ooKuxIWCIkrc6FYMcYogrgxoEHFeRFRE42w5D/X73dv1i4pUOiGmkly4/u9779c979x7z3sKSZLwK02JX2y/BYCXwmeESybyGV0Mo6YQNTBzf38f09/fj7GxMRwcHPyQnTk5OSEpKQm5ublQqVTvxdCfXwIg9fT0YGBgAO7u7qipqUFAQACurq7Q29uLoaEhXhgdHY3q6mqo1WocHx+jpaUF8/PzPJeamor8/HwKhKWlJbS2tmJ/f5/nsrKyUFhYSK8vhG8+BmD2j7Dm5mZotVqcnp5ibW0N4eHhcHFxQUREBM7OznhsZ2cHu7u7iI2Nhb29PQOi8b29PaysrECpVCIqKgpubm4IDAzE7OwsLi8vsbW1hYyMDIrVK/yTUQDd3d2oqKjgjygFc3NzCAsLg7OzMyIjI3F+fo7V1VVsbm5ie3sbMTExsLW15acMYmFhAbe3twza1dUVwcHB0Gg0WF9fR15eHsXqNAZA3wUJCQkoKipiGilIQ0MDf2xmZsYUJicn87rp6Wmm+OLigpmglIWEhPDc4OAg+vr6cH19zSwUFBR8tVa4BhITE03aauPj4/QIE75gFMBPanmjAFT05ycxYNRU8svo6CiGh4fR2dkJoQvw8PBAXV0dfHx8cHNzw+MjIyO8Ni4uDpWVlbCxseGibWpqwuLiIs9lZ2cjJycHlpaW3DlTU1N6afhfABMTE+jq6uLgnp6eqK+v5+BU2aQTcvD4+HhUVVXB2toaJycnrAdy8MzMTNYDasnl5WUeIzA6eyWc0GiNdkFbWxvvlIKKzvxs57IYGQYnMWpsbNSLEQWibqHgBIiA2dnZIS0tDbW1taxlwm0o3YYp1zNwd3fHSlheXs4MUO+TElJaZCUsKyuDubk5q9xjJaTd02/ISkgAqR1JCw4PD+XNSiZvQysrKygUClhYWDCrpAX+/v7o6OjQiOkA4RpdGi4/Y+Cp5uDggJKSEj5HiAkCQSmU2T06OlILuadikURqbgXAt+K9khlIT0/nc+ApRqceSe63/FZQUBDa29vp9W9mICUlhU/DJ10slP/Vs6+vLx9gZNRRGxsb3JJeXl76td7e3vrPiIEPYmEEtdrk5CRR9V0AHB0dUVpaitDQUD0gOmGJEV0NUAEeGVxU3gn/CwLAS7qUSCYwUf2SOOSk4uJi+vdYuJtwtfA/6AQgpxR81N1WnIU//4EKbP7w8PBGPJ9REersTHTchaE8G3bBvs6fZHJLiwBW4vakJfr9/Py4JIx+IFNhAqf6em2QkT7hysfr/hVgAIhbr+v/xmSzAAAAAElFTkSuQmCC'

var navbar, newElement;
var titleEl = document.getElementById('title-media-strip');
var p = titleEl.getElementsByTagName('table')[0]
if (!p){
	titleEl = document.getElementById('tn15content')
	var p = titleEl.getElementsByTagName('div')[0]
}

var year = document.getElementById('tn15title').getElementsByTagName('a')[0].text

var iFrame = create('iframe', {
	src: mmLocation + link + id + '/?year='+year,
	frameborder: 0,
	scrolling: 'no' 
})

var popup = create('div', { 
	id: 'mmPopup', 
	onclick: function(){
		popup.innerHTML = '<strong>Movie Manager:</strong>';
		popup.appendChild(iFrame);
	},
	innerHTML: '<strong>Movie Manager:</strong><a href="#"><img src="'+img+'" />Add movie</a>'
});

p.parentNode.insertBefore(popup, p);
