var Quality = new Class({
			
	initialize: function(container, types, existing){
		var self = this
		
		this.container = $(container)
		this.list = this.container.getElement('.customList')
		
		// Save changes in this textarea
		this.json = new Element('textarea', {'name':'Quality.templates'}).inject(this.container, 'top')
		
		// Create type list
		this.qualityTypes = new Element('select', {
			'events': {
				'change': self.saveQualityTemplate.bind(self)
			}
		});
		$each(types, function(type){
			new Element('option', {
				'value': type.key,
				'text': type.label
			}).inject(self.qualityTypes)
		})
		
		if(existing)
			$each(existing, function(item){
				self.add(item)
			});
		
	},
	
	add: function(properties){
		var self = this

		var template = new Element('div', {
			'class': 'template',
			'data-id': properties.id
		}).adopt(
			new Element('h4', {'text': properties.name}),
			new Element('span', {
				'class':'delete',
				'html': '<img src="/media/images/delete.png" alt="Delete" />',
				'events': {
					'click': function(e){
						(e).stop()
						this.getParent('.template').destroy()
						self.saveQualityTemplate()
					}
				}
			}),
			new Element('div', {
				'class': 'ctrlHolder'
			}).adopt(
				new Element('label', {'text':'Name'}),
				new Element('input', {
					'type':'text', 
					'class': 'name textInput large', 
					'value': properties.name,
					'events': {
						'change': self.saveQualityTemplate.bind(self),
						'keyup': function(e){
							template.getElement('h4').set('text', e.target.get('value'))
							self.saveQualityTemplate()
						}
					}
				})
			),
			new Element('div', {
				'class': 'ctrlHolder'
			}).adopt(
				new Element('label', {'text':'Wait'}),
				new Element('input', {
					'type':'text', 
					'class': 'waitFor textInput xsmall', 
					'value': properties.waitFor,
					'events': {
						'change': self.saveQualityTemplate.bind(self),
						'keyup': self.saveQualityTemplate.bind(self)
					}
				}),
				new Element('span', {'text':' day(s) for better quality.'})
			),
			new Element('div', {
				'class': 'ctrlHolder'
			}).adopt(
				new Element('label', {'text': 'Qualities'}),
				self.temptype = new Element('div', {'class':'types'}).adopt(
					new Element('div', {
						'class': 'header'
					}).adopt(
						new Element('span', {'class':'qualityType','text': 'Search for'}),
						new Element('span', {'class':'markComplete', 'html': '<acronym title="Won\'t download anything else if it has found this quality.">Finish</acronym>'})
					)
				),
				new Element('a', {
					'text': 'Add another quality to search for.',
					'href': '#',
					'class': 'addType',
					'events': {
						'click': function(e){
							(e).stop()
							self.addType(template)
						}
					}
				})
			)
		).inject(this.list)
		
		if(properties.types)
			$each(properties.types, function(type){
				self.newType(type).inject(self.temptype)
			})
		
		self.makeSortable(template.getElement('.types'))
		self.saveQualityTemplate()

	},
	
	addType: function(template){
		var self = this
		
		var properties = {
			'type': '',
			'markComplete': true
		}
		
		var type = self.newType(properties).inject(template.getElement('.types'))
		template.getElement('.types').retrieve('sortable').addItems(type)
		
		self.saveQualityTemplate()
		
	},
	
	newType: function(properties){
		var self = this
		
		if(!properties){
			var properties = {
				'id': '',
				'type': '',
				'markComplete': true
			}
		}
		
		return new Element('div', {
			'class': 'item',
			'data-id': properties.id
		}).adopt(
			new Element('span', {
				'class':'qualityType'
			}).adopt(
				self.qualityTypes.clone().cloneEvents(self.qualityTypes).set('value', properties.type)
			),
			new Element('span', {
				'class':'markComplete'
			}).adopt(
				new Element('input', {
					'type':'checkbox',
					'class':'markComplete',
					'checked': properties.markComplete,
					'events': {
						'click': self.saveQualityTemplate.bind(self)
					}
				})
			),
			new Element('span', {
				'class':'delete',
				'html': '<img src="/media/images/delete.png" alt="Delete" />',
				'events': {
					'click': function(e){
						(e).stop()
						if(this.getParent('.types').getElements('.item').length == 1)
							var makeNew = this.getParent('.template')
						
						this.getParent('.item').destroy()
						
						if(makeNew)
							self.addType(makeNew)
							
						self.saveQualityTemplate()
						
					}
				}
			}),
			new Element('span', {
				'class':'handle'
			})
		).highlight()
		
	},
	
	saveQualityTemplate: function(){
		var self = this
		var templateJson = []
		
		this.container.getElements('.template').each(function(template){
			
			var temp = {
				'id': template.get('data-id'),
				'name': template.getElement('input.name').get('value'),
				'waitFor': template.getElement('input.waitFor').get('value'),
				'types': []
			}

			template.getElements('.types .item').each(function(type){
				temp.types.extend([{
					'id': type.get('data-id'),
					'type': type.getElement('select').get('value'), 
					'markComplete': type.getElement('input[type=checkbox]').get('checked')
				}])
			})
			
			templateJson.extend([temp])
		});

		this.json.set('value', JSON.encode(templateJson))
		
	},
	
	makeSortable: function(el){
		var self = this
		var sort = new Sortables(el, {
			'revert': true,
			'clone': true,
			'handle': '.handle',
			'opacity': 0.5,
			'onComplete': self.saveQualityTemplate.bind(this, [el])
		});	
		el.store('sortable', sort);
	}

})