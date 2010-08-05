var Uniform = new Class( {
	Implements : [ Options ],

	options : {
		validClass : 'valid',
		invalidClass : 'invalid',
		focusedClass : 'focused',
		holderClass : 'ctrlHolder',
		fieldSelector : 'input, select, textarea'
	},

	initialize : function(options) {
		this.setOptions(options);

		var focused = this.options.focusedClass;
		var holder = '.' + this.options.holderClass;

		$$('.uniForm ' + this.options.fieldSelector).addEvents( {
			'focus' : function() {
				var parent = this.getParent(holder);
				if (parent)
					parent.addClass(focused);
			},
			'blur' : function() {
				var parent = this.getParent(holder);
				if (parent)
					parent.removeClass(focused);
			}
		});
	}
});