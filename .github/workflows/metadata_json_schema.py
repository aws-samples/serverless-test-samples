METADATA = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "$id": "http://example.com/example.json",
    "type": "object",
    "title": "Sample schema for ServerlessLand metadata.json files",
    "description": "This JSON document describes a sub-repo for displaying on ServerlessLand.",
    "required": ["title", "description", "content_language","language","type","diagram",
                 "framework","services","git_repo_url","pattern_source",
                 "pattern_detail_tabs","authors"],
    "properties": {
        "title": {
            "$id": "#/properties/title",
            "type": "string",
            "title": "The sub-repo title",
            "examples": ["Python Starter Project"],
            "maxLength": 128,
            "minLength": 10
        },
        "description": {
            "$id": "#/properties/description",
            "type": "string",
            "title": "The sub-repo description",
            "examples": ["This project contains automated test sample code samples for serverless applications written in Python."],
            "maxLength": 1028,
            "minLength": 10
        },
        "content_language": {
            "$id": "#/properties/content_language",
            "type": "string",
            "title": "Repository Written Language",
            "examples": ["English","Spanish"],
            "maxLength": 60,
            "minLength": 3
        },
        "language": {
            "$id": "#/properties/language",
            "type": "string",
            "title": "Repository Programming Language",
            "examples": [".NET","Python"],
            "pattern": ".NET|Java|Python|TypeScript|Go|Rust",
            "maxLength": 60,
            "minLength": 3
        },
        "type": {
            "$id": "#/properties/type",
            "type": "array",
            "title": "Test Types Implemented",
            "examples": [["Unit"],["Unit","Integration"]],
            "minItems": 1,
            "uniqueItems": True,
            "items": {
                "type": "string",
                "pattern": "Unit|Integration|Load|Canary",
                }
        },
        "diagram": {
            "$id": "#/properties/diagram",
            "type": "string",
            "title": "Achitecture or Test Diagram for the pattern",
            "examples": ["/img/xray.png"],
            "maxLength": 2048,
            "minLength": 3
        },   
        "framework": {
            "$id": "#/properties/framework",
            "type": "string",
            "title": "Deployment Framework for the pattern",
            "examples": ["SAM"],
            "pattern": "SAM|Cloudformation|CDK",
            "maxLength": 60,
            "minLength": 3
        },      
        "services": {
            "$id": "#/properties/services",
            "type": "array",
            "title": "AWS Services used in the pattern",
            "examples": [["apigw","lambda","dynamodb"]],
            "minItems": 1,
            "uniqueItems": True,
            "items": {
                "type": "string",
                "minLength": 2
                }
        },
        "git_repo_url": {
            "$id": "#/properties/git_repo_url",
            "type": "string",
            "title": "URL of the git repo",
            "examples": ["https://github.com/aws-samples/serverless-test-samples"],
            "pattern": "https://github.com/aws-samples/serverless-test-samples",
            "maxLength": 2048,
            "minLength": 3
        },   
        "pattern_source": {
            "$id": "#/properties/pattern_source",
            "type": "string",
            "title": "Contributor of the the pattern",
            "examples": ["AWS"],
            "pattern": "AWS|Customer",
            "maxLength": 60,
            "minLength": 3
        },  
        "pattern_detail_tabs": {
            "$id": "#/properties/pattern_detail_tabs",
            "type": "array",
            "title": "Detail links to key files, from sub-repo root",
            "minItems": 1,
            "uniqueItems": True,
            "items": {
                "type": "object",
                "required": ["title","filepath"],
                "properties": {
                    "title": {
                        "$id": "#/properties/pattern_detail_tabs/properties/title",
                        "type": "string",
                        "title": "Title of the key file",
                        "examples": ["Application Code","Unit Tests - Emulator"],
                        "maxLength": 128,
                        "minLength": 3
                    }, 
                    "filepath": {
                        "$id": "#/properties/pattern_detail_tabs/properties/filepath",
                        "type": "string",
                        "title": "File path of the key file from sub-project root",
                        "examples": ["/src/app.py","/tests/unit/local_emulator_test.py"],
                        "maxLength": 128,
                        "minLength": 3
                    }
                }
            }
        },
        "authors": {
            "$id": "#/properties/authors",
            "type": "array",
            "title": "About the authors",
            "minItems": 1,
            "uniqueItems": True,
            "items": {
                "type": "object",
                "required": ["name","bio"],
                "properties": {
                    "name": {
                        "$id": "#/properties/authors/properties/name",
                        "type": "string",
                        "title": "Author Name",
                        "examples": ["Sara Tester","Joe Programmer"],
                        "maxLength": 2048,
                        "minLength": 3
                    }, 
                    "image": {
                        "$id": "#/properties/authors/properties/image",
                        "type": "string",
                        "title": "URL to a hosted image of the author",
                        "examples": ["https://www.linkedin.com/in/exampleperson/mypicture.png"],
                        "maxLength": 4096,
                        "minLength": 3,
                        "pattern": "https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\\b([-a-zA-Z0-9()@:%_\+.~#?&\/=]*)"
                    }
                    , 
                    "bio": {
                        "$id": "#/properties/authors/properties/bio",
                        "type": "string",
                        "title": "More about the author",
                        "examples": ["Principal Solutions Architect at AWS"],
                        "maxLength": 2048,
                        "minLength": 3
                    }
                    , 
                    "linkedin": {
                        "$id": "#/properties/authors/properties/linkedin",
                        "type": "string",
                        "title": "URL to LinkedIn Account",
                        "examples": [ "https://www.linkedin.com/in/exampleperson/"],
                        "maxLength": 4096,
                        "minLength": 3,
                        "pattern": "https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\\b([-a-zA-Z0-9()@:%_\+.~#?&\/=]*)"
                    }
                    , 
                    "twitter": {
                        "$id": "#/properties/authors/properties/twitter",
                        "type": "string",
                        "title": "Twitter handle for author",
                        "examples": ["https://twitter.com/exampleperson"],
                        "maxLength": 4096,
                        "minLength": 3,
                        "pattern": "https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\\b([-a-zA-Z0-9()@:%_\+.~#?&\/=]*)"
                    }
                }
            }
        },

    },
}