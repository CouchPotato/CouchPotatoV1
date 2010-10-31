var MovieList = new Class({
	
	initialize: function(){
		
		
		
	}
	
})

var Movie = new Class({
	
	initialize: function(){
		
		
		
	}
	
})

var FormBuilder = new Class({
	
	_row: function(options){
		var row = new Element('div', {
			'class': 'row'
		})
		this._addOptions(row, options)
		return row
	},
	
	_input: function(type, options){
		var input = new Element('input', {
			'type': type
		})
		this._addOptions(input, options)
		
		return input
	},
	
	_select: function(name, options){
		var select = new Element('select', {
			'name': name
		})
		this._addOptions(select, options)
		
		return select
	},
	
	_submit: function(label, name){

		return new Element('div').adopt(
			new Element('a', {
				'href': '#',
				'class':'submit',
				'html': label,
				'name': name
			}),
			new Element('input', {
				'type': 'submit',
				'name': name
			}).hide()
		)

	},
	
	_addOptions: function(element, options){
		if(options)
			$each(options, function(value, option){
				element.set(option, value)
			})
	}
	
});

var MovieSearch = new Class({
	
	Implements: [Options, FormBuilder],
	
	options: {
		'url': null,
		'quality': null
	},
	
	initialize: function(container, options){
		var self = this;
		self.setOptions(options);
		
		// Main options
		self.container = $(container)
		self.requestUrl = self.options.url
		
		// Create Form
		self.createForm()
		
		// Set some options and styles
		self.overText()
		self.hideResults()
		
	},
	
	createForm: function(){
		var self = this;
		
		self.form = new Element('form', {
			'class': 'addNew',
			'method': 'post'
		}).adopt(
			self._row().adopt(
				self.undo = new Element('a', {
					'href': '#',
					'class': 'undo',
					'title': 'No good, undo!'
				}).addEvent('click', function(e){
					(e).stop()
					self.reset()
				})
			),
			self._row().adopt(
				self.movie = self._input('text', {
					'name':'movie',
					'title':'Movie Title'
				})
			),
			self._row().adopt(
				self.results = self._select('result').addEvent('change', self.selectMovie.bind(self))
			),
			self._row().adopt(
				self.year = self._input('text', {
					'name':'year',
					'title':'Year'
				})
			),
			self._row().adopt(
				self.add = self._submit('Add &raquo;', 'add').addEvent('click', function(e){
					(e).stop()
					self.form.fireEvent('submit')
				})
			)
		).inject(self.container);
		
		// Add quality items
		//self.addQualities()
		
		self.form.addEvent('submit', self.onSubmit.bind(self))
		self.spinner = new Spinner(self.form)

		return self.form
		
	},
	
	onSubmit: function(e){
		var self = this;
		if(e) e.stop()

		self.spinner.show()
		this.request = new Request.JSON({
			'url': self.requestUrl,
			'data': self.form,
			'onComplete': self.onComplete.bind(self)
		}).send()
		
	},
	
	onComplete: function(json){
		var self = this;
		
		self.showResults()
		self.addResults(json.results)
		self.selectMovie()
		self.spinner.hide()
	},
	
	showResults: function(){
		this.form.addClass('results')
		this.undo.getParent().show()
		this.results.getParent().show()
		this.movie.getParent().hide()
		OverText.update();
	},
	
	hideResults: function(){
		this.form.removeClass('results')
		this.undo.getParent().hide()
		this.results.getParent().hide()
		this.movie.getParent().show()
		this.showYear(false)
		OverText.update();
	},
	
	addResults: function(results){
		var self = this;

		results.each(function(item, nr){
			var option = new Element('option', {
				'value': item.imdb,
				'text': item.name + (item.year ? ' ('+item.year+')' : ''),
				'year': item.year
			}).inject(self.results)
		})
	},
	
	selectMovie: function(){
		var self = this;
		var selected = self.results.getElement('option[value='+self.results.get('value')+']')
		
		self.showYear(!selected.get('year'))
	},
	
	showYear: function(bool){
		if(bool)
			this.year.getParent().show()
		else
			this.year.getParent().hide()
	},
	
	reset: function(){
		var self = this;
		
		self.results.empty()
		self.year.set('value', '')
		self.movie.set('value', '')
		self.hideResults()
	},
	
	overText: function(){
		var self = this;
		new OverText(self.movie);
		new OverText(self.year);
	}
	
});

MovieSearch.Filters = new Class.Singleton({
	
	queue: [],

	add: function(filter){
		this.queue.include(filter);
	},
	
	get: function(){
		return this.queue
	}
	
});
