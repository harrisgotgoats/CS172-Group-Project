package com.example.demo;

import java.io.File;
import java.io.IOException;
import java.nio.file.Path;



import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.util.QueryBuilder;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;



@SpringBootApplication
@RestController

public class DemoApplication {

    public static IndexSearcher isearcher;
    public static QueryBuilder builder;
	public static IndexSearcher setupIndex() throws IOException
    {
        //Get directory data for the index "cs172 java lucene\Data"
        String userDir = System.getProperty("user.dir");
        String indexDir = userDir + "\\Index";

        //Define IndexSearcher
        Path path = (new File(indexDir)).toPath();
        Directory indexDirectory = FSDirectory.open(path); 
        DirectoryReader ireader = DirectoryReader.open(indexDirectory);
        IndexSearcher isearcher = new IndexSearcher(ireader);



        return isearcher;
    }
	public static void main(String[] args) throws IOException {
		SpringApplication.run(DemoApplication.class, args);
		try{
			isearcher = setupIndex();

            StandardAnalyzer analyzer = new StandardAnalyzer(); //has to match the analyzer in indexer.java
            builder = new QueryBuilder(analyzer); // builder that makes query objects
		}catch(IOException e) {
            System.out.println("An I/O Error Occurred..!!");
        }

	}

    //http://localhost:8080/search?query=Alex 
    @GetMapping("/search")
    public String do_search(@RequestParam(value = "query", defaultValue = "Justin") String query) throws IOException
    {
        String field = "content";
        Query q = builder.createPhraseQuery(field, query);
        ScoreDoc[] hits = isearcher.search(q, 10).scoreDocs;

        String searchResults = "";
        for (int i = 0; i < hits.length; i++) {
            Document hitDoc = isearcher.doc(hits[i].doc);

            String url = hitDoc.get("url");
            String title = hitDoc.get("title");
            searchResults+= title + " ["+url+"]\n";
        }
        return searchResults;
    }

	@GetMapping("/hello") //use the "hello" method at http://localhost:8080/hello?name=yourname 
    public String hello(@RequestParam(value = "name", defaultValue = "World") String name) {
    return String.format("Hello %s!", name);
	
    }

}
