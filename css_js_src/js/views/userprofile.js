$(document).ready( function () { 
	modelReadyObj.schema_callback = function() {
		UserprofileItemView = ItemView.extend({
			templatename : "userprofile",
			modeltype: Userprofile
		});

		UserprofileListView = ListView.extend({
			el: '.userprofile-view',
			collection: UserprofileContainer,
			item: UserprofileItemView
		});

		var userprofile_view = new UserprofileListView();
		userprofile_view.trigger('render');
	}

	modelReadyObj.callback_defined();
});
