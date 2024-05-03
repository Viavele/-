import time
import json
from typing import Optional, Any
from hashlib import sha256


class Block:
    def __init__(self, timestamp: Optional[float] = None, data: Optional[Any] = None):
        self.index = 1
        self.previous_hash = None
        self.timestamp = timestamp or time.time()
        self.timestamp = str(self.timestamp)
        self.data = [] if data is None else data
        self.difficulty = 4
        # NONCE - номер, который можно использовать лишь раз
        self.nonce = 0
        self.hash = self.get_hash()

    def __repr__(self):
        return json.dumps({'index': self.index, 'previous_hash': self.previous_hash,
                           'timestamp': self.timestamp, 'data': self.data,
                           'difficulty': self.difficulty, 'nonce': self.nonce,
                           'hash': self.hash})

    def get_hash(self) -> str:
        hashed = sha256()
        # sha256().update(data) - данные должны быть bytes-like объектом
        # для этого используем str().encode('utf-8')
        # str().encode('utf-8') -> bytes
        hashed.update(str(self.previous_hash).encode('utf-8'))
        hashed.update(str(self.timestamp).encode('utf-8'))
        hashed.update(str(self.data).encode('utf-8'))
        hashed.update(str(self.nonce).encode('utf-8'))
        return hashed.hexdigest()

    # 'Proof-of-work реализация'
    def mine(self, difficulty: int):
        while Block().is_hypotenuse(int(self.hash[:difficulty + 2], 16)) != True:
            # делаем новый хэш
            self.nonce += 1
            self.hash = self.get_hash()

    # проверяем, является ли число гипотенузой
    # в худшем случае алгоритм работает за O(num ** (1/2))
    def is_hypotenuse(self, num):
        sqr_num = int(num ** (1/2))
        if int(sqr_num) ** 2  != num:
            sqr_num += 1
        checks = []
        for i in range(1, sqr_num):
            if num - (i ** 2) in checks:
                return True
            else:
                checks.append(i ** 2)
        return False


class BlockChain:
    def __init__(self):
        self.chain = [Block(time.time())]
        # майним даже первый блок
        self.chain[0].mine(Block().difficulty)

    def __repr__(self) -> str:
        # для красивого вывода
        return json.dumps([{'index': item.index, 'previous_hash': item.previous_hash,
                            'timestamp': item.timestamp, 'data': item.data,
                            'difficulty': item.difficulty, 'nonce': item.nonce,
                            'hash': item.hash} for item in self.chain])

    def get_last_block(self) -> Block:
        return self.chain[len(self.chain) - 1]

    def add_block(self, block: Block):
        block.previous_hash = self.get_last_block().hash
        # обновляем хэш
        block.hash = block.get_hash()
        block.mine(Block().difficulty)
        block.index = len(self.chain) + 1
        self.chain.append(block)

    def is_valid(self) -> bool:
        # начинаем с 1, ибо не имеем блоков перед нулевым блоком
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # проверяем хэши в блокчейне
            if current_block.hash != current_block.get_hash() or \
                    previous_block.hash != current_block.previous_hash:
                return False

        return True
