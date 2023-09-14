// full adder
module full_adder(
    input a, b, cin,
    output sum, cout
);
    // 单 bits 的全加器实现：
    // assign sum = a ^ b ^ cin;
    // assign cout = a & b | a & cin | b & cin;
    
    // 跟上面两行代码的功能是一样的
    // 而且它还有个优势：它适用于任何位数的输入 a 和 b
    assign {cout, sum} = a + b + cin;
endmodule
