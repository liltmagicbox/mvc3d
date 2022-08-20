import json
import zlib

def compress(string):
	1
def main():
    x = zlib.compress('message'.encode('utf-8'))

    #===compress sqeuence
    dict_message = {'ham':1,'egg':12}
    json_message = json.dumps(dict_message)
    byte_message = json_message.encode('utf-8')
    comp_message = zlib.compress(byte_message)

    byte_message = zlib.decompress(comp_message)
    json_message = byte_message.decode('utf-8')
    dict_message = json.loads(json_message)
    print(dict_message)
    #===compress sqeuence



#===no need to compress
#print(byte_message)
#print(comp_message)
#b'{"ham": 1, "egg": 12}'
#b'x\x9c\xabV\xcaH\xccU\xb2R0\xd4QPJMO\x07\xb1\x8cj\x01>\x9a\x05~'
#note: smallsize,seems no need to compress!
#===no need to compress


#===what is byte code??
#byte_message = 'a'.encode()
#b'x\x9cK\x04\x00\x00b\x00b' a
#b'x\x9cKL\x04\x00\x01%\x00\xc3' aa
#b'x\x9cKL$\x12\x00\x00Fu\x0f\x8a' aaa
#b'x\x9cKL$\x12$\x01\x00Va\x0f\xec' aaaaa...

#33 is b''.__sizeof__().
# \xabc... is len =3.

#b'x\x9cK\x04\x00\x00b\x00b' a
#size is 33+9 = 42.   seems of: 9cK 4 0 0b 0b
#b'    b'
#===what is byte code??