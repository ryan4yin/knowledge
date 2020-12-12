>2018-01-25

开启、关闭、读、写 操作，都必须捕获或向上游抛出可能存在的异常 IOException 

可以使用try-with-resources语句自动关闭资源（仅限实现了 AutoCloseable 接口的类，而且应该将其与 try-catch 语句分离，使代码更清晰。），使代码更简洁。

### 一、各种流

1. 基类：所有子类都基于这四个派生。前缀是功能，后缀是基类。 

    a. 字节流（直接写入，不存在内部缓冲） 
        1. InputStream 
        1. OutputStream 

    b. 字符流（实际上是对字节流的包装，因为需要对字符做编解码，所以有一个内部缓冲，需要flush） 
        1. Reader 
        1. Writer 

1. 字符流： 
    1. 读写（使用系统默认的字符集，因此不推荐使用。若需要指定字符集，应该用 字节流+转换流） 
        1. FileReader 
            - 提供的方法比较少，没有python方便。 
        1. FileWriter 
            - 默认是直接覆盖。但可附带一个是否 add 的bool可选项。 

    1. 缓冲区：使用缓冲，高效执行读写操作 
        1. BufferReader 
                - 可以按行读取。 
                - 带行号的子类：LineNumberReader 
        1. BufferWriter 
            - 有跨平台的换行写入方法。 

1. 字节流： 
    1. 读写 
        1. FileInputStream 
        1. FileOutputStream 
    1. 缓冲区： 
        1. BufferedInputStream 
        1. BufferedOutputStream 
            - 它的 write 方法在接收一个int值时，会写出该int值的低8位（一个byte）。 
            - 它的 read 方法也会返回一个 int 值，这和 write 是匹配的。使用 int 是为了表示读取失败的情况。java 用 int 值 -1 表示 false。（因此在自己实现这个类时，要注意 byte 提升到 int 时的位拓展方式的问题。） 

 1. 转换流（字符流与字节流之间的转换，**还有指定字符集**，字符集的名字是大小写不敏感的） 
    1. 读入：InputStreamReader 
    1. 输出：OutputStreamWriter 

1. 打印流： 
     - 增强了流的输出功能，可以方便的自定义格式。 
     - System.out是一个打印流，它的print、printf、println方法，都是打印流里定义的。 
     - 以下两个打印流的api完全类似 
        1. PrintStream 
        1. PrintWriter 
            - 差别在于，PrintWriter 的构造器，可以接收多种类型的参数：
                1. File 对象 
                1. String 文件路径 
                1. 字节输出流 OutputStream  （内部会自动创建转换流，并使用默认字符集将Unicode字符转换成字节再输出） 
                1. 字符输出流 Writer 

1. SequenceInputStream 序列流 
    将多个流有序串联起来，从第一个流开始读取，到达文件末尾后，继续读取第二个流，如此直至最后一个流读到末尾。 

 1. 数据流：用于读写基本数据类型 
    1. DataInputStream 
    1. DataOutputStream 

 

1. java.Util.Scanner类： 
    用于从流中按类型读取数据。一般来说比 DataInputStream 更好用一点。 

1. 两个只操作数组，不使用io资源的流，因此不需要调用close方法。严格来说不能算io流。 
    1. 字节数组流： 
        1. ByteArrayInputStream：构造时需要接收一个数据源（byte 数组） 
        1. ByteArrayOutputStream：其实就相当于一个具有缓冲区，能自动分配内存的数组。不过不能用索引查询，也不能删除数据。但可以直接转换成基本类型的 byte 数组（从这点来说，比ArrayList<Byte>要方便）。 

    1. 字符数组流： 。。。


### 流对象的选用规律

1. 明确 **源** 和 **目的**： 
    1. 源：InputStream  Reader 
    1. 目的：OutputStream  Writer 

1. 数据是否纯文本，从 1 的结果中二选一 
    1. 是：字符流 
    1. 否：字节流 
1. 明确源和目的所属的对象 
    1. 源： 
        a. 文件：FileReader  FileInputStream 
        b. 标准输入流：System.in  是InputStream对象 
    1. 目的： 
        a. 文件：FileWriter  FileOutputStream 
        b. 标准输出流：System.out  是OutputStream的子类对象 

1. 是否需要转换流，或者指定字符集 
    - 选择对应的转换流 

1. 是否需要添加缓冲（加快效率） 
    - 选择对应的缓冲