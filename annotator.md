# Contents #




# Introduction #

The AmCAT Annotator is the new name for iNet. A tool to perform manual codings of Article text, on article and sentence level.
It is build around the concept of Codingjobs. Codingjobs are assigned to a coder and contain one or more articles. A codingjob also contains one or two AnnotationSchema (for Article-level codings and for Sentence/Unit-level codings), that determines which AnnotationSchemaFields the coder has to code.
See the [Object Model](ObjectModel#Coding.md) description for more information.

# Technical Overview #

When the coding page is loaded, a background call via AJAX is made to load all the fields in the AnnotationSchema, including all the possible values they can have.
A distinction is made between Ontology fields and normal fields. Ontology fields usually contain many possible values (sometimes more than 1000), therefore it is more efficient to send them only one time from the server to the client, and not separately for each AnnotationSchemaField they are used in.

[WvA: Is dat onderscheid nu niet verdwenen??]

Example of JSON Field data. `items-key` refers to the `ontologies` dictionary.
```
{
    "fields": [
        {
            "isOntology": true, 
            "showAll": false, 
            "fieldname": "Vorm", 
            "id": "159", 
            "items-key": 10020
        }, 
        {
            "items": [
                {"value": 0, "label": "0"}, 
                {"value": 1, "label": "1"}
            ], 
            "showAll": true, 
            "fieldname": "Irrelevant", 
            "id": "158", 
            "isOntology": false
        }, 
        [...]
    "ontologies": 
        {
        "10019": [
            {"value": 19238, "label": "0: ASS"}, 
            {"value": 19239, "label": "1: REA"}, 
            {"value": 19240, "label": "2: IDE"}, 
            {"value": 19241, "label": "3: ACT"}, 
            [...]
        ],
        "10020": [
            {"value": 19248, "label": "1: nieuwsbericht"}, 
            {"value": 19249, "label": "2: achtergrond"}, 
            {"value": 19250, "label": "3: personen in het nieuws"}
        ]
    }
}
```


At the same time the table with all the articles is loaded via AJAX. This table is rendered using the DataTables library.
When the coder clicks on an article (or uses the next/previous buttons), the Article text is loaded as separate sentences.

```
{
    "articleid": "36857549", 
    "sentences": [
        {"text": "Obama zingt zijn toespraken", "id": 8866742, "unit": "1.1"},
        {"text": "Eerste zin lead", "id": 8866743, "unit": "2.1"},
        {"text": "Tweede zin lead", "id": 8866744, "unit": "2.2"},
        {"text": "Verdere zinnen lead", "id": 8866745, "unit": "2.3"}
    ]
}
```

[WvA: Hoeveel hiervan zou eigenlijk via de API kunnen / moeten?]

If the codingjob contains an AnnotationSchema on the Article level, this data is loaded at the same time via AJAX.
The response is a standard HTML Django form. The JavaScript code will insert jQuery-ui AutoComplete widgets to the fields that have any `items` (see JSON code above).

If the codingjob contains an AnnotationSchema on the sentence/unit level, this data is loaded as well via AJAX.
For efficiency reasons this data is loaded as JSON. The JavaScript code is responsible of making a normal table of it. This is not a DataTable, because performance turned out to be very bad when many codings are present (as in hundreds).
All codings are send with their text (human-readable) values. This is easier to process, since the data can be displayed directly, else all the items would have to be looked up in the `items` list of the field.
The JSON data also contains an HTML table row which all the fields, that is being filled with the existing codings to create the table. In addition there is an "Add new row" button on each row and a hidden `codingid` field, that contains the ID of the coding. When the coder adds a new row, this value is called 'new-1', 'new-2', etc. And after saving it will be changed to a real ID (from the database). There is also a hidden input for each field, for the ID of the current value.
If the user clicks on an input field in the table, the AutoComplete widget is added to this field. When the coder selects a value from the AutoComplete widget the hidden input corresponding to the input field is filled with the ID of the selected choice.

```
{
    "unitcodingFormTablerow": 
    "<tr><td><input type=\"text\" name=\"unit\" value=\"\" /><input type=\"hidden\" name=\"unit-hidden\" value=\"\" /></td><input type=\"text\" name=\"field_166\" id=\"id_field_166\" /><input type=\"hidden\" name=\"field_166-hidden\" /></td><td><button class=\"add-row-button\" title=\"Add a new row\">Add</button><input type=\"hidden\" name=\"codingid\" value=\"\" /></td></tr>", 
    "unitcodings": {
        "headers": ["id", "sentence", "Source", "Subject", "Predicate", "Quality", "Type", "Object", "Angle"], 
        "rows": [
            [9884, 8866744, "experts, onderzoekers", "obama, barack, president vs", "als het ware zingt", "0.5", "2: IDE", "arbeidsduurverkorting", null]
        ]
    }
}
```

The AmCAT Annotator tracks the forms to see where any changes have been made. Only the modified sentence codings are send to the server, as for all the article codings, iff a change has been made to any article coding.
The comment and article status will also be send to the server when they have been changed. All these changes are send as one POST request to the server.
The article codings and comment/status forms are send as normal JSON dictionaries, with the fieldnames as key.
The sentence codings are split into a list of new, updated and deleted codings. For deleted codings only the codingid is provided. For the new/updated codings only the IDs of the selected values are send to the server. Before sending a check is made on each field to see if the text value corresponds to the ID in the hidden field. If the hidden field is empty and the text value is a valid one (based on the possible values in the field), the hidden field is updated.

```
{
    "commentAndStatus": {"comment":"","status":"9"},
    "articlecodings":{
        "field_157":"sdf",
        "field_158":"",
        "field_159":19248
    },
    "unitcodings":{
        "delete":[],
        "modify":[
            {
                "codingid":"9884",
                "unit":"8866744",
                "field_161":"2077",
                "field_162":"10859",
                "field_163":"als het ware zingt",
                "field_164":"1",
                "field_165":"19240",
                "field_166":"654",
                "field_167":""
            }
        ],
        "new":[]
    }
}
```


# Missing functionality #
Certain functionality is not implemented yet, such as the ability to add/edit articles, add new sentences and to split an article.