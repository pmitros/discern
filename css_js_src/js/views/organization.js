$(document).ready( function () { 
	modelReadyObj.schema_callback = function() {
		OrganizationItemView = ItemView.extend({
			templatename : "organization",
			modeltype: Organization
		});

		OrganizationListView = ListView.extend({
			el: '.organization-view',
			collection: OrganizationContainer,
			item: OrganizationItemView
		});

		var organization_view = new OrganizationListView();
		organization_view.trigger('render');
	}
	 
	modelReadyObj.callback_defined();
});
