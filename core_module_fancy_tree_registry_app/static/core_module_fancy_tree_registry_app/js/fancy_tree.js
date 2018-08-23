var fancy_tree_select_handler = function(event, data){
	var values = [];
    var nodes = data.node.tree.getSelectedNodes();
    $(nodes).each(function() {
        values.push($(this)[0].key);
    });

	// Collect data
    var module_data = {
        'data[]': values
    }

    var module = $(data.originalEvent.currentTarget).closest(".module");
    saveModuleData(module, module_data);
};

// .ready() called.
$(function() {
    // bind event to fancy_tree_ready_event calls
    $(document).on("fancy_tree_select_event", function(event, data){
        fancy_tree_select_handler(event, data);
    });
});