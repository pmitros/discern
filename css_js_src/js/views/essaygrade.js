$(document).ready( function () { 
	modelReadyObj.schema_callback = function() {
		EssaygradeItemView = ItemView.extend({
			templatename : "essaygrade",
			modeltype: Essaygrade
		});

		EssaygradeListView = ListView.extend({
			el: '.essaygrade-view',
			collection: EssaygradeContainer,
			item: EssaygradeItemView
		});

		var essaygrade_view = new EssaygradeListView();
		essaygrade_view.trigger('render');
	}

	modelReadyObj.callback_defined();
});
