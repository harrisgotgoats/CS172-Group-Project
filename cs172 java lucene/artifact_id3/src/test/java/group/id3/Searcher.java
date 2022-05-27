package group.id3;

import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TermQuery;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;

import static org.junit.Assert.assertEquals;

import java.io.File;
import java.io.IOException;
import java.nio.file.Path;

import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.search.Explanation;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.util.IOUtils; 
import org.apache.lucene.util.QueryBuilder;



//References:
//** 
// https://lucene.apache.org/core/9_1_0/core/index.html
// **


public class Searcher {

    //StandardQueryParser queryParser;
    Query query;
    IndexSearcher searcher;
    //QueryParser queryParser;


    public Searcher(String indexDirectoryPath) throws IOException {
        Directory indexDirectory = FSDirectory.open(new File(indexDirectoryPath).toPath());
        //searcher = new IndexSearcher(indexDirectory);

    }

    public static void main(String[] args) throws IOException {
        
        String userDir = System.getProperty("user.dir");
        String indexDir = userDir + "\\Data";
        //Searcher searcher = new Searcher(indexDir);

        //Define IndexSearcher
        Path path = (new File(indexDir)).toPath();
        Directory indexDirectory = FSDirectory.open(path); 
        DirectoryReader ireader = DirectoryReader.open(indexDirectory);
        IndexSearcher isearcher = new IndexSearcher(ireader);

        
        //make the Query
        StandardAnalyzer analyzer = new StandardAnalyzer();
        QueryBuilder builder = new QueryBuilder(analyzer); // builder that makes query objects

        String field = "content";
        String queryText = "Justin";
        Query q = builder.createPhraseQuery(field, queryText);

        //get Query results
        ScoreDoc[] hits = isearcher.search(q, 10).scoreDocs; //get query results, max 10
        //assertEquals(1, hits.length);
        System.out.println("hits length "+ hits.length);
        System.out.println("Search Results for: "+queryText);

        //Print Query Results
        for (int i = 0; i < hits.length; i++) {
            Document hitDoc = isearcher.doc(hits[i].doc);
            System.out.println(hitDoc.get("url"));
          }

        //first Document content
        //Document firstDoc = isearcher.doc(hits[0].doc);
        //System.out.println("content of firstDoc"+firstDoc.get("content")+"\n");
        
        Explanation exp = isearcher.explain(q,0);
        System.out.println("explanation of firstDoc+n"+exp.toString());


        ireader.close();
        indexDirectory.close();
        //IOUtils.rm(path); //removes the entire index







        /*
        StandardQueryParser qpHelper = new StandardQueryParser();
        StandardQueryConfigHandler config =  qpHelper.getQueryConfigHandler();
        config.setAllowLeadingWildcard(true);
        config.setAnalyzer(new WhitespaceAnalyzer());
        Query query = qpHelper.parse("apache AND lucene", "defaultField");*/
    }
}
