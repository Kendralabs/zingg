package zingg.spark.core.documenter;

import org.apache.spark.sql.Column;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.types.DataType;

import freemarker.template.Version;
import zingg.common.client.Arguments;
import zingg.common.core.Context;
import zingg.common.core.documenter.ModelDocumenter;
import zingg.common.core.documenter.RowWrapper;

/**
 * Spark specific implementation of ModelDocumenter
 *
 */
public class SparkModelDocumenter extends ModelDocumenter<SparkSession, Dataset<Row>, Row, Column,DataType> {

	private static final long serialVersionUID = 1L;

	public SparkModelDocumenter(Context<SparkSession, Dataset<Row>, Row, Column,DataType> context, Arguments args) {
		super(context, args);
		super.modelColDoc = new SparkModelColDocumenter(context,args);
	}

	@Override
	public RowWrapper<Row> getRowWrapper(Version v) {
		return new SparkRowWrapper(v);
	}

}
