#coding:utf-8

from string import Template

nav_root_template = Template(r"""
<div id="leftcolumn" class="edoBox">
 <dl class="portlet portlet-navigation-tree">
    <dt class="portletHeader">
        <a class="title" href="${root_url}">${root_title}</a>
    </dt>
    <dd class="portletItem">
        <ul class="portletNavigationTree navTreeLevel0">
            ${nav_items}
            <!--p class="navTreeItem visualNoMarker" 
               tal:repeat="node items" 
               tal:replace="structure node">
            </p-->
        </ul>
    </dd>
    <dd class="portletFooter">
        <div><!-- --></div>
    </dd>
  </dl>

</div>
""")

nav_item_template = Template(r"""
<li class="navTreeItem visualNoMarker ${class_str}" 
    kssattr:nodeurl="${node_url}">
    <div class="visualIcon contenttype-folder">
        <a border="0" class="visualIconPadding 
        ${a_class_str}" name="${node_name}"
            href="${node_url}" onfocus="this.blur()">
        ${node_title}
            </a>
    </div>
    ${children_str}
</li>
""")
        #<img src="${icon_src}" href="" border="0" />
