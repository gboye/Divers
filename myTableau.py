def myTableau(*args):
    """Test of the python macro system"""
#get the doc from the scripting context which is made available to all scripts
    desktop = XSCRIPTCONTEXT.getDesktop()
    model = desktop.getCurrentComponent()
#check whether there's already an opened document. Otherwise, create a new one
    if not hasattr(model, "Sheets"):
        model = desktop.loadComponentFromURL(
            "private:factory/scalc","_blank", 0, () )
#get the XText interface
    sheet = model.Sheets.getByIndex(0)
#create an XTextRange at the end of the document
    listCellNames = [l+str(c) for l in "ABCD" for c in range(1,20)]
#and set the number in the cell
    for numEl,element in enumerate(listCellNames):
        cell=sheet.getCellRangeByName(element)
        cell.setValue(numEl)
    return None
