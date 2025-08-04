from mcp.server.fastmcp import FastMCP
import os
import fitz 

## TODO create server

mcp=FastMCP("DocumentServer")

## TODO Create and define TOOL

@mcp.tool()
def read_document(file_path:str)->str:
    """Retrieve the content of a document give its file path"""
    
    try:    
        if not os.path.exists(file_path):
            return f"Error: file path {file_path} does not exist"
        # page_number_list=[9,10,20]
        # content=""
        # doc=fitz.open(file_path)
        
        # for page_num in page_number_list:
        #     if 0 >= page_num < len(doc):
        #         page=doc[page_num]
        #         content+=page.get_text()
        page_number_list=[9,10,20]
        doc=fitz.open(file_path)
        content=""

        for page_number in page_number_list:


            if 0 <=  page_number < len(doc):
                page = doc[page_number]

            else:
                print(f"Page {page_number} doesn't exist in the document")

            if page :

                content += page.get_text()
                print(type(content))

        #print(content)
        return content    
   
        # if not os.path.exists(file_path):
        #     return f"Error: File {file_path} does not exist."
        # with open(file_path, 'r') as file:
        #     content = file.read()
        # return content

    except Exception as e:
        print(e)
        return f"Error reading file {str(e)}"
    
if __name__ == "__main__":
    mcp.run(transport="stdio")

    