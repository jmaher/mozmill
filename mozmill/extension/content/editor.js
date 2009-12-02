var editor = {
  index : 0,

  tabs : [],

  currentTab : null,

  width : 500,
  
  height : 700,

  init : function(width, height) {
    this.width = width;
    this.height = height;
    this.openNew();
  },

  resize : function(width, height) {
    this.width = width;
    this.height = height;
    this.reloadSize();
  },

  reloadSize : function() {
    if(this.currentTab) {
      this.currentTab.iframeElement.style.width = this.width + "px";
      this.currentTab.iframeElement.style.height = this.height + "px";
      if(this.currentTab.editorElement) {
        this.currentTab.editorElement.style.width = (this.width - 20) + "px";
        this.currentTab.editorElement.style.height = (this.height - 20) + "px";
      }
    }
  },

  switchTab : function(index) {
    if(!index)
      index = this.tabs.length - 1;
    if(index < 0)
      return;
    if(this.currentTab)
      this.currentTab.iframeElement.style.display = "none";
    this.index = index;
    this.currentTab = this.tabs[index];
    this.reloadSize();
    this.currentTab.iframeElement.style.display = "block";
  },

  closeCurrentTab : function() {
    this.currentTab.destroy();
    this.currentTab = '';
    this.tabs.splice(this.index, 1);
    this.switchTab();
  },

  openNew : function(content, filename) {
    var newTab = new editorTab(content, filename);
    this.tabs.push(newTab);
    // will switch to new tab when the iframe has loaded
  },

  getContent : function() {
    return this.currentTab.getContent();
  },

  getFilename : function() {
    return this.currentTab.filename;
  }
}


function editorTab(content, filename) {
  var iframeElement = document.createElement("iframe");
  iframeElement.className = "editor-frame";
  var editorObject = this;

  iframeElement.addEventListener("load", function() {
    var win = iframeElement.contentWindow;
    win.onEditorLoad = function() {
      editorObject.editorElement = win.document.getElementById("editor");
      editorObject.editor = win.editor;
      if(content)
        win.editor.setContent(content);
      editor.reloadSize();
      editor.switchTab();
    } // this function is invoked by the iframe
  }, true);
  iframeElement.src = "oldeditor.html";
  document.getElementById("editors").appendChild(iframeElement);

  this.iframeElement = iframeElement;
  this.filename = filename;
}

editorTab.prototype = {
  initFromFile : function(file) {
    this.editor.setContent(FileIO.read(file));
    this.fileName = file;
  },

  setContent : function(content) {
    this.editor.setContent(content);
  },

  getContent : function() {
    return this.editor.getContent();
  },

  saveToFile : function() {
    var file = this.fileName;
    if (!file.exists())
      FileIO.create(file); 
    FileIO.write(file, this.editor.getContent(), 'w');
  },

  saveAs : function(fileName) {
    this.fileName = fileName;
    this.saveToFile;
  },

  destroy : function() {
    this.iframeElement.parentNode.removeChild(this.iframeElement);
  }
}
