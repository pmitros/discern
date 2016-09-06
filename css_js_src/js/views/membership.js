$(document).ready( function () { 
	modelReadyObj.schema_callback = function() {
		MembershipItemView = ItemView.extend({
			templatename : "membership",
			modeltype: Membership
		});

		MembershipListView = ListView.extend({
			el: '.membership-view',
			collection: MembershipContainer,
			item: MembershipItemView
		});

		var membership_view = new MembershipListView();
		membership_view.trigger('render');
	}

	modelReadyObj.callback_defined();
});
