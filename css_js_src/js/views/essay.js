$(document).ready( function () { 
	modelReadyObj.schema_callback = function() {
		// console.log("essay callback called");
		EssayItemView = ItemView.extend({
			templatename : "essay",
			modeltype: Essay
		});

		EssayListView = ListView.extend({
			el: '.essay-view',
			collection: EssayContainer,
			item: EssayItemView
		});

		var essay_view = new EssayListView();
		essay_view.trigger('render');
	};

	modelReadyObj.callback_defined();
});
