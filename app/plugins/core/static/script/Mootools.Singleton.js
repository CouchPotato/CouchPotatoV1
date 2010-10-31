/*
---

script: Class.Singleton.js

description: Defines a singleton Class.

license: MIT-style license.

authors:
- Eneko Alonso

requires:
- core:1.2.4/Class

provides: [Class.Singleton]

...
*/

Class.Singleton = new Class({

	initialize: function(classDefinition, classOptions){
		this.singletonClass = new Class(classDefinition);
		this.classOptions = classOptions;
	},

	getInstance: function() {
		return this.instance || new this.singletonClass(this.classOptions);
	}

});
