$(document).ready( function () { 
	modelReadyObj.schema_callback = function() {
		ProblemItemView = ItemView.extend({
			templatename : "problem",
			modeltype: Problem
		});

		ProblemListView = ListView.extend({
			el: '.problem-view',
			collection: ProblemContainer,
			item: ProblemItemView
		});

		var problem_view = new ProblemListView();
		problem_view.trigger('render');
	}

	modelReadyObj.callback_defined();
});
