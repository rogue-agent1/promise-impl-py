class Promise:
    PENDING,FULFILLED,REJECTED=0,1,2
    def __init__(self,executor=None):
        self.state=self.PENDING; self.value=None; self.callbacks=[]
        if executor:
            try: executor(self._resolve,self._reject)
            except Exception as e: self._reject(e)
    def _resolve(self,value):
        if self.state!=self.PENDING: return
        self.state=self.FULFILLED; self.value=value
        for cb,_,p in self.callbacks: self._handle(cb,p)
    def _reject(self,reason):
        if self.state!=self.PENDING: return
        self.state=self.REJECTED; self.value=reason
        for _,eb,p in self.callbacks: self._handle(eb,p)
    def _handle(self,fn,p):
        if fn is None: (p._resolve if self.state==self.FULFILLED else p._reject)(self.value); return
        try: p._resolve(fn(self.value))
        except Exception as e: p._reject(e)
    def then(self,on_fulfilled=None,on_rejected=None):
        p=Promise()
        if self.state==self.PENDING: self.callbacks.append((on_fulfilled,on_rejected,p))
        elif self.state==self.FULFILLED: self._handle(on_fulfilled,p)
        else: self._handle(on_rejected,p)
        return p
    def catch(self,on_rejected): return self.then(None,on_rejected)
    @staticmethod
    def resolve(value):
        p=Promise(); p._resolve(value); return p
    @staticmethod
    def all(promises):
        results=[None]*len(promises); count=[0]
        def make(p):
            def executor(resolve,reject):
                for i,pr in enumerate(promises):
                    def cb(v,idx=i):
                        results[idx]=v; count[0]+=1
                        if count[0]==len(promises): resolve(results)
                    pr.then(cb,reject)
            return executor
        return Promise(make(None))
if __name__=="__main__":
    log=[]
    p=Promise.resolve(42).then(lambda v: v*2).then(lambda v: log.append(v))
    assert log==[84]
    p2=Promise(lambda res,rej: rej(Exception("err")))
    errs=[]
    p2.catch(lambda e: errs.append(str(e)))
    assert errs==["err"]
    print(f"Promise: {log}, errors: {errs}")
    print("All tests passed!")
